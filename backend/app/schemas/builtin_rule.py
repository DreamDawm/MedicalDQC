import uuid
from datetime import datetime

from pydantic import BaseModel


class BuiltinRuleResponse(BaseModel):
    id: uuid.UUID
    expectation_type: str
    display_name: str
    category: str
    description: str
    parameters_schema: dict
    usage_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
