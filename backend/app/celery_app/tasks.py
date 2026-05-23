from datetime import datetime

from app.celery_app.celery_config import celery_app
from app.database import SessionLocal
from app.models.datasource import Datasource
from app.models.builtin_rule import BuiltinRule
from app.models.validation_rule import ValidationRule
from app.models.validation_task import ValidationTask
from app.models.validation_result import ValidationResult
from app.services.gx_engine import run_expectations


def add_log(result_record, message: str, db) -> None:
    """添加日志条目并保存到数据库"""
    if result_record.logs is None:
        result_record.logs = []
    result_record.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    db.commit()


def update_progress(result_record, progress: int, db) -> None:
    """更新进度并保存到数据库"""
    result_record.progress = progress
    db.commit()


@celery_app.task(bind=True)
def run_validation_task(self, task_id: str):
    db = SessionLocal()
    try:
        task = db.query(ValidationTask).filter(
            ValidationTask.id == task_id
        ).first()
        if not task:
            return {"error": "Task not found"}

        ds = db.query(Datasource).filter(
            Datasource.id == task.datasource_id
        ).first()

        result_record = ValidationResult(
            task_id=task.id,
            status="running",
            progress=0,
            logs=[],
        )
        db.add(result_record)
        db.commit()

        add_log(result_record, f"开始执行校验任务: {task.name}", db)
        update_progress(result_record, 5, db)

        rules = db.query(ValidationRule).filter(
            ValidationRule.id.in_(task.rule_ids),
            ValidationRule.enabled == True,
        ).all()

        add_log(result_record, f"找到 {len(rules)} 条校验规则", db)
        update_progress(result_record, 10, db)

        tables_expectations = {}
        for rule in rules:
            builtin = db.query(BuiltinRule).filter(
                BuiltinRule.id == rule.builtin_rule_id
            ).first()
            table = rule.table_name
            if table not in tables_expectations:
                tables_expectations[table] = []

            kwargs = {**rule.parameters}
            if rule.column_name:
                kwargs["column"] = rule.column_name
            if rule.mostly is not None:
                kwargs["mostly"] = rule.mostly

            tables_expectations[table].append({
                "expectation_type": builtin.expectation_type,
                "display_name": builtin.display_name,
                "kwargs": kwargs,
            })

        add_log(result_record, f"需校验 {len(tables_expectations)} 个表", db)
        update_progress(result_record, 15, db)

        all_results = []
        total_tables = len(tables_expectations)
        current_table_idx = 0

        for table, expectations in tables_expectations.items():
            add_log(result_record, f"开始校验表: {table} ({len(expectations)} 条规则)", db)

            table_result = run_expectations(
                db_type=ds.db_type,
                host=ds.host,
                port=ds.port,
                database=ds.database,
                username=ds.username,
                password=ds.password,
                table_name=table,
                expectations=expectations,
            )
            all_results.extend(table_result["results"])

            passed = sum(1 for r in table_result["results"] if r["success"])
            failed = len(table_result["results"]) - passed
            add_log(result_record, f"表 {table} 校验完成: 通过 {passed}, 失败 {failed}", db)

            current_table_idx += 1
            progress = 15 + int((current_table_idx / total_tables) * 75)
            update_progress(result_record, progress, db)

        passed = sum(1 for r in all_results if r["success"])
        failed = len(all_results) - passed

        add_log(result_record, "开始生成报告", db)
        update_progress(result_record, 90, db)

        report_path = None
        try:
            from app.services.report_service import generate_html_report
            report_path = generate_html_report(task.name, all_results)
            add_log(result_record, f"报告已生成: {report_path}", db)
        except ImportError:
            add_log(result_record, "报告服务不可用，跳过报告生成", db)

        result_record.status = "success" if failed == 0 else "failed"
        result_record.finished_at = datetime.utcnow()
        result_record.total_expectations = len(all_results)
        result_record.passed_count = passed
        result_record.failed_count = failed
        result_record.result_detail = {"results": all_results}
        result_record.report_path = report_path
        result_record.progress = 100
        db.commit()

        add_log(result_record, f"任务完成: 状态={result_record.status}, 通过={passed}, 失败={failed}", db)

        return {"status": result_record.status, "passed": passed, "failed": failed}

    except Exception as e:
        if 'result_record' in locals():
            add_log(result_record, f"任务执行出错: {str(e)}", db)
            result_record.status = "error"
            result_record.finished_at = datetime.utcnow()
            result_record.result_detail = {"error": str(e)}
            db.commit()
        return {"error": str(e)}
    finally:
        db.close()
