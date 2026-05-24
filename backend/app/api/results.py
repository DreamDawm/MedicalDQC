import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.validation_result import ValidationResult
from app.schemas.validation_result import ResultResponse, TrendDataPoint

router = APIRouter()


@router.get("", response_model=list[ResultResponse])
def list_results(
    task_id: uuid.UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(ValidationResult)
    if task_id:
        query = query.filter(ValidationResult.task_id == task_id)
    query = query.order_by(ValidationResult.started_at.desc())
    return query.offset((page - 1) * page_size).limit(page_size).all()


@router.get("/trend", response_model=list[TrendDataPoint])
def get_trend(
    task_id: uuid.UUID | None = None,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    query = db.query(
        func.date(ValidationResult.started_at).label("date"),
        func.avg(
            ValidationResult.passed_count * 100.0
            / func.nullif(ValidationResult.total_expectations, 0)
        ).label("pass_rate"),
        func.count().label("total_runs"),
    ).filter(ValidationResult.status == "success")
    if task_id:
        query = query.filter(ValidationResult.task_id == task_id)
    query = query.group_by(func.date(ValidationResult.started_at))
    query = query.order_by(func.date(ValidationResult.started_at))
    rows = query.all()
    return [
        {"date": str(r.date), "pass_rate": round(r.pass_rate, 2), "total_runs": r.total_runs}
        for r in rows
    ]


@router.get("/{result_id}", response_model=ResultResponse)
def get_result(result_id: uuid.UUID, db: Session = Depends(get_db)):
    result = db.query(ValidationResult).filter(
        ValidationResult.id == result_id
    ).first()
    if not result:
        raise HTTPException(404, "结果不存在")
    return result


@router.get("/{result_id}/report")
def download_report(result_id: uuid.UUID, db: Session = Depends(get_db)):
    result = db.query(ValidationResult).filter(
        ValidationResult.id == result_id
    ).first()
    if not result or not result.report_path:
        raise HTTPException(404, "报告不存在")
    report_path = result.report_path.replace("\\", "/")
    return FileResponse(report_path, filename="report.html")


@router.get("/{result_id}/report/view")
def view_report(result_id: uuid.UUID, db: Session = Depends(get_db)):
    result = db.query(ValidationResult).filter(
        ValidationResult.id == result_id
    ).first()
    if not result or not result.report_path:
        raise HTTPException(404, "报告不存在")
    report_path = result.report_path.replace("\\", "/")
    return FileResponse(
        report_path,
        media_type="text/html",
        headers={"Content-Disposition": "inline"}
    )


@router.delete("/{result_id}")
def delete_result(result_id: uuid.UUID, db: Session = Depends(get_db)):
    result = db.query(ValidationResult).filter(
        ValidationResult.id == result_id
    ).first()
    if not result:
        raise HTTPException(404, "结果不存在")

    # 删除报告文件
    if result.report_path and os.path.exists(result.report_path):
        os.remove(result.report_path)

    # 删除数据库记录
    db.delete(result)
    db.commit()
    return {"status": "deleted"}
