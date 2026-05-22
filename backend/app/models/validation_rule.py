import uuid
from datetime import datetime

from sqlalchemy import String, Float, Boolean, DateTime, JSON, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ValidationRule(Base):
    __tablename__ = "validation_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    datasource_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("datasources.id")
    )
    table_name: Mapped[str] = mapped_column(String(200))
    column_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    builtin_rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("builtin_rules.id")
    )
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    mostly: Mapped[float | None] = mapped_column(Float, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="warning")
    row_condition: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
