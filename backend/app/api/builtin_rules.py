import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.builtin_rule import BuiltinRule
from app.schemas.builtin_rule import BuiltinRuleResponse

router = APIRouter()


@router.get("", response_model=list[BuiltinRuleResponse])
def list_rules(db: Session = Depends(get_db)):
    return db.query(BuiltinRule).order_by(
        BuiltinRule.usage_count.desc()
    ).all()


@router.get("/{rule_id}", response_model=BuiltinRuleResponse)
def get_rule(rule_id: uuid.UUID, db: Session = Depends(get_db)):
    rule = db.query(BuiltinRule).filter(BuiltinRule.id == rule_id).first()
    if not rule:
        raise HTTPException(404, "规则不存在")
    return rule
