from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class InsightBase(BaseModel):
    account_name: str
    insight_text: str
    product_area: str
    product_subcategory: str
    insight_category: str
    input_data_source: Optional[str] = None
    source_tool: str
    source_link: Optional[str] = None
    role_present: Optional[str] = None
    conversation_type: Optional[str] = None
    date_of_record: date
    comments: Optional[str] = None
    dedup_group_key: Optional[str] = None
    unique_insight_status: str = "Key Record"


class InsightCreate(InsightBase):
    signal_id: Optional[UUID] = None
    account_id: Optional[UUID] = None
    pipeline_run_id: Optional[UUID] = None


class InsightResponse(InsightBase):
    id: UUID
    signal_id: Optional[UUID] = None
    account_id: Optional[UUID] = None
    pipeline_run_id: Optional[UUID] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class InsightListResponse(BaseModel):
    items: list[InsightResponse]
    total: int
    page: int
    page_size: int


class InsightFilters(BaseModel):
    product_area: Optional[str] = None
    insight_category: Optional[str] = None
    account_name: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    unique_insight_status: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=200)
