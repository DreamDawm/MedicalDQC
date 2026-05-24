import uuid
from datetime import datetime

from sqlalchemy.orm.attributes import flag_modified

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
    # 创建新的 list 以触发 SQLAlchemy 变更检测
    # 日志格式: [YYYY-MM-DD HH:MM:SS] 消息内容
    result_record.logs = result_record.logs + [f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"]
    flag_modified(result_record, "logs")
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

        add_log(result_record, f"========== 开始执行校验任务 ==========", db)
        add_log(result_record, f"任务名称: {task.name}", db)
        add_log(result_record, f"数据源: {ds.name} ({ds.db_type})", db)
        add_log(result_record, f"数据库地址: {ds.host}:{ds.port}/{ds.database}", db)
        update_progress(result_record, 5, db)

        rules = db.query(ValidationRule).filter(
            ValidationRule.id.in_(task.rule_ids),
            ValidationRule.enabled == True,
        ).all()

        add_log(result_record, f"启用规则数量: {len(rules)} 条", db)
        for i, rule in enumerate(rules, 1):
            builtin = db.query(BuiltinRule).filter(
                BuiltinRule.id == rule.builtin_rule_id
            ).first()
            add_log(result_record, f"  规则 {i}: {builtin.display_name} - 表[{rule.table_name}] 列[{rule.column_name or '全表'}]", db)
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
                "rule_id": rule.id,
            })

        add_log(result_record, f"需校验表数量: {len(tables_expectations)} 个", db)
        update_progress(result_record, 15, db)

        all_results = []
        total_tables = len(tables_expectations)
        current_table_idx = 0

        for table, expectations in tables_expectations.items():
            add_log(result_record, f"----------------------------------------", db)
            add_log(result_record, f"开始校验表: {table}", db)
            add_log(result_record, f"  规则数量: {len(expectations)} 条", db)

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

            # 详细记录每个规则的执行结果
            for r in table_result["results"]:
                exp_info = next((e for e in expectations if e["expectation_type"] == r["expectation_type"]), None)
                rule_display = exp_info.get("display_name", r["expectation_type"]) if exp_info else r["expectation_type"]
                col_info = r["kwargs"].get("column", "全表")
                status = "✓ 通过" if r["success"] else "✗ 失败"
                # 尝试获取记录数信息
                result_detail = r.get("result", {})
                element_count = result_detail.get("element_count", "N/A")
                unexpected_count = result_detail.get("unexpected_count", 0)
                if element_count != "N/A" and isinstance(element_count, int):
                    passed_count = element_count - unexpected_count
                    add_log(result_record, f"  [{status}] {rule_display} - 列[{col_info}] | 记录数: {element_count}, 通过: {passed_count}, 失败: {unexpected_count}", db)
                else:
                    add_log(result_record, f"  [{status}] {rule_display} - 列[{col_info}]", db)

            passed = sum(1 for r in table_result["results"] if r["success"])
            failed = len(table_result["results"]) - passed
            add_log(result_record, f"表 {table} 校验完成: 通过 {passed} 条, 失败 {failed} 条", db)

            current_table_idx += 1
            progress = 15 + int((current_table_idx / total_tables) * 75)
            update_progress(result_record, progress, db)

        passed = sum(1 for r in all_results if r["success"])
        failed = len(all_results) - passed

        add_log(result_record, f"----------------------------------------", db)
        add_log(result_record, f"========== 校验汇总 ==========", db)
        add_log(result_record, f"总校验规则: {len(all_results)} 条", db)
        add_log(result_record, f"通过: {passed} 条", db)
        add_log(result_record, f"失败: {failed} 条", db)
        add_log(result_record, f"通过率: {(passed/len(all_results)*100):.1f}%", db)

        add_log(result_record, f"开始生成报告...", db)
        update_progress(result_record, 90, db)

        report_path = None
        try:
            from app.services.report_service import generate_html_report
            report_path = generate_html_report(task.name, all_results)
            add_log(result_record, f"报告已生成: {report_path}", db)
        except ImportError:
            add_log(result_record, f"报告服务不可用，跳过报告生成", db)

        # 将 UUID 转换为字符串，以便 JSON 序列化
        def convert_uuids(obj):
            if isinstance(obj, dict):
                return {k: convert_uuids(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_uuids(item) for item in obj]
            elif isinstance(obj, uuid.UUID):
                return str(obj)
            return obj

        serializable_results = convert_uuids(all_results)

        result_record.status = "success" if failed == 0 else "failed"
        result_record.finished_at = datetime.now()
        result_record.total_expectations = len(all_results)
        result_record.passed_count = passed
        result_record.failed_count = failed
        result_record.result_detail = {"results": serializable_results}
        result_record.report_path = report_path
        result_record.progress = 100
        flag_modified(result_record, "result_detail")
        db.commit()

        add_log(result_record, f"========== 任务完成 ==========", db)
        add_log(result_record, f"最终状态: {result_record.status}", db)

        return {"status": result_record.status, "passed": passed, "failed": failed}

    except Exception as e:
        if 'result_record' in locals():
            try:
                db.rollback()
                add_log(result_record, f"========== 任务执行出错 ==========", db)
                add_log(result_record, f"错误信息: {str(e)}", db)
                result_record.status = "error"
                result_record.finished_at = datetime.now()
                result_record.result_detail = {"error": str(e)}
                db.commit()
            except Exception:
                db.rollback()
        return {"error": str(e)}
    finally:
        db.close()
