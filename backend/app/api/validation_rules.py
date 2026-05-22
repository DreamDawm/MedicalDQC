import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.validation_rule import ValidationRule
from app.models.builtin_rule import BuiltinRule
from app.schemas.validation_rule import (
    ValidationRuleCreate, ValidationRuleUpdate, ValidationRuleResponse,
)

router = APIRouter()


@router.post("", response_model=ValidationRuleResponse)
def create_rule(data: ValidationRuleCreate, db: Session = Depends(get_db)):
    rule = ValidationRule(**data.model_dump())
    db.add(rule)
    builtin = db.query(BuiltinRule).filter(
        BuiltinRule.id == data.builtin_rule_id
    ).first()
    if builtin:
        builtin.usage_count += 1
    db.commit()
    db.refresh(rule)
    return rule


@router.get("", response_model=list[ValidationRuleResponse])
def list_rules(
    datasource_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(ValidationRule)
    if datasource_id:
        query = query.filter(ValidationRule.datasource_id == datasource_id)
    return query.all()


@router.put("/{rule_id}", response_model=ValidationRuleResponse)
def update_rule(
    rule_id: uuid.UUID, data: ValidationRuleUpdate, db: Session = Depends(get_db)
):
    rule = db.query(ValidationRule).filter(ValidationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(404, "校验规则不存在")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(rule, key, val)
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}")
def delete_rule(rule_id: uuid.UUID, db: Session = Depends(get_db)):
    rule = db.query(ValidationRule).filter(ValidationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(404, "校验规则不存在")
    db.delete(rule)
    db.commit()
    return {"message": "已删除"}
