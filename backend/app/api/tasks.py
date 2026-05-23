import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.validation_task import ValidationTask
from app.schemas.validation_task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()


@router.post("", response_model=TaskResponse)
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    task_data = data.model_dump()
    # Convert UUID objects to strings for JSON serialization
    task_data["rule_ids"] = [str(rid) for rid in task_data.get("rule_ids", [])]
    task = ValidationTask(**task_data)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("", response_model=list[TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(ValidationTask).all()


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: uuid.UUID, data: TaskUpdate, db: Session = Depends(get_db)
):
    task = db.query(ValidationTask).filter(
        ValidationTask.id == task_id
    ).first()
    if not task:
        raise HTTPException(404, "任务不存在")
    update_data = data.model_dump(exclude_unset=True)
    # Convert UUID objects to strings for JSON serialization
    if "rule_ids" in update_data:
        update_data["rule_ids"] = [str(rid) for rid in update_data["rule_ids"]]
    for key, val in update_data.items():
        setattr(task, key, val)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(task_id: uuid.UUID, db: Session = Depends(get_db)):
    task = db.query(ValidationTask).filter(
        ValidationTask.id == task_id
    ).first()
    if not task:
        raise HTTPException(404, "任务不存在")
    db.delete(task)
    db.commit()
    return {"message": "已删除"}


@router.post("/{task_id}/run")
def trigger_task(task_id: uuid.UUID, db: Session = Depends(get_db)):
    task = db.query(ValidationTask).filter(
        ValidationTask.id == task_id
    ).first()
    if not task:
        raise HTTPException(404, "任务不存在")

    # 异步提交任务，不等待结果
    from app.celery_app.tasks import run_validation_task
    run_validation_task.delay(str(task_id))

    # 立即返回，不等待 Celery 响应
    return {"message": "任务已提交"}
