import uuid
from datetime import datetime

from pydantic import BaseModel


class DatasourceCreate(BaseModel):
    name: str
    db_type: str
    host: str
    port: int
    database: str
    username: str
    password: str


class DatasourceUpdate(BaseModel):
    name: str | None = None
    host: str | None = None
    port: int | None = None
    database: str | None = None
    username: str | None = None
    password: str | None = None


class DatasourceResponse(BaseModel):
    id: uuid.UUID
    name: str
    db_type: str
    host: str
    port: int
    database: str
    username: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TableInfo(BaseModel):
    table_name: str


class ColumnInfo(BaseModel):
    column_name: str
    data_type: str
    is_nullable: bool
