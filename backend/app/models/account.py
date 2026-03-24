import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.db import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default="gen_random_uuid()")
    sfdc_account_id = Column(String(18), unique=True, nullable=True)
    account_name = Column(String(255), nullable=False, unique=True)
    icp = Column(String(100))
    vertical = Column(String(100))
    stage = Column(String(100))
    opportunity_amount = Column(Numeric(15, 2))
    workloads = Column(Text)
    gpu_types = Column(Text)
    gpu_quantities = Column(Text)
    use_case = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
