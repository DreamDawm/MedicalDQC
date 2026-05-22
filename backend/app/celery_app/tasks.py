from datetime import datetime

from app.celery_app.celery_config import celery_app
from app.database import SessionLocal
from app.models.datasource import Datasource
from app.models.builtin_rule import BuiltinRule
from app.models.validation_rule import ValidationRule
from app.models.validation_task import ValidationTask
from app.models.validation_result import ValidationResult
from app.services.gx_engine import run_expectations


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
        )
        db.add(result_record)
        db.commit()

        rules = db.query(ValidationRule).filter(
            ValidationRule.id.in_(task.rule_ids),
            ValidationRule.enabled == True,
        ).all()

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
                "kwargs": kwargs,
            })

        all_results = []
        for table, expectations in tables_expectations.items():
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

        passed = sum(1 for r in all_results if r["success"])
        failed = len(all_results) - passed

        report_path = None
        try:
            from app.services.report_service import generate_html_report
            report_path = generate_html_report(task.name, all_results)
        except ImportError:
            pass

        result_record.status = "success" if failed == 0 else "failed"
        result_record.finished_at = datetime.utcnow()
        result_record.total_expectations = len(all_results)
        result_record.passed_count = passed
        result_record.failed_count = failed
        result_record.result_detail = {"results": all_results}
        result_record.report_path = report_path
        db.commit()

        return {"status": result_record.status, "passed": passed, "failed": failed}

    except Exception as e:
        if 'result_record' in locals():
            result_record.status = "error"
            result_record.finished_at = datetime.utcnow()
            result_record.result_detail = {"error": str(e)}
            db.commit()
        return {"error": str(e)}
    finally:
        db.close()
