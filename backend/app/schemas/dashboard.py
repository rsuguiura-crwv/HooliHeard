from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_insights: int
    key_records: int
    total_accounts: int
    sources_active: int


class AreaCount(BaseModel):
    product_area: str
    count: int


class CategoryCount(BaseModel):
    insight_category: str
    count: int


class AccountCount(BaseModel):
    account_name: str
    count: int


class TrendPoint(BaseModel):
    week: str
    count: int
