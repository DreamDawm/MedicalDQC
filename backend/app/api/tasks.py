import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.validation_task import ValidationTask
from app.schemas.validation_task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()


@router.post("", response_model=TaskResponse)
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    task = ValidationTask(**data.model_dump())
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
    for key, val in data.model_dump(exclude_unset=True).items():
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
    from app.celery_app.tasks import run_validation_task
    celery_task = run_validation_task.delay(str(task_id))
    return {"message": "任务已提交", "celery_task_id": celery_task.id}
