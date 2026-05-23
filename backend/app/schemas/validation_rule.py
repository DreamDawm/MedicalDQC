import uuid
from datetime import datetime

from pydantic import BaseModel


class ValidationRuleCreate(BaseModel):
    datasource_id: uuid.UUID
    table_name: str
    column_name: str | None = None
    builtin_rule_id: uuid.UUID
    parameters: dict = {}
    mostly: float | None = None
    severity: str = "warning"
    row_condition: str | None = None
    enabled: bool = True


class ValidationRuleUpdate(BaseModel):
    table_name: str | None = None
    column_name: str | None = None
    builtin_rule_id: uuid.UUID | None = None
    parameters: dict | None = None
    mostly: float | None = None
    severity: str | None = None
    row_condition: str | None = None
    enabled: bool | None = None


class ValidationRuleResponse(BaseModel):
    id: uuid.UUID
    datasource_id: uuid.UUID
    table_name: str
    column_name: str | None
    builtin_rule_id: uuid.UUID
    parameters: dict
    mostly: float | None
    severity: str
    row_condition: str | None
    enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
