import uuid
from datetime import datetime

from pydantic import BaseModel


class TaskCreate(BaseModel):
    name: str
    datasource_id: uuid.UUID
    rule_ids: list[uuid.UUID] = []
    schedule_cron: str | None = None
    is_active: bool = True


class TaskUpdate(BaseModel):
    name: str | None = None
    rule_ids: list[uuid.UUID] | None = None
    schedule_cron: str | None = None
    is_active: bool | None = None


class TaskResponse(BaseModel):
    id: uuid.UUID
    name: str
    datasource_id: uuid.UUID
    rule_ids: list
    schedule_cron: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
