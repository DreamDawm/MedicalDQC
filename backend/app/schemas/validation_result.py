import uuid
from datetime import datetime

from pydantic import BaseModel


class ResultResponse(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    status: str
    started_at: datetime
    finished_at: datetime | None
    total_expectations: int
    passed_count: int
    failed_count: int
    result_detail: dict
    report_path: str | None
    progress: int = 0
    logs: list = []

    model_config = {"from_attributes": True}


class TrendDataPoint(BaseModel):
    date: str
    pass_rate: float
    total_runs: int
