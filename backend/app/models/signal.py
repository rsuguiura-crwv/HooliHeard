import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.db import Base


class Signal(Base):
    __tablename__ = "signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default="gen_random_uuid()")
    source_tool = Column(String(50), nullable=False)
    source_type = Column(String(50))
    source_link = Column(Text)
    account_name = Column(String(255), nullable=True)
    raw_content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON)
    ingested_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    pipeline_run_id = Column(UUID(as_uuid=True), nullable=True)
