from sqlalchemy import func, extract
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.insight import Insight
from app.schemas.dashboard import (
    AccountCount,
    AreaCount,
    CategoryCount,
    DashboardSummary,
    TrendPoint,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
    total_insights = db.query(func.count(Insight.id)).scalar() or 0
    key_records = (
        db.query(func.count(Insight.id))
        .filter(Insight.unique_insight_status == "Key Record")
        .scalar()
        or 0
    )
    total_accounts = db.query(func.count(func.distinct(Insight.account_name))).scalar() or 0
    sources_active = db.query(func.count(func.distinct(Insight.source_tool))).scalar() or 0
    return DashboardSummary(
        total_insights=total_insights,
        key_records=key_records,
        total_accounts=total_accounts,
        sources_active=sources_active,
    )


@router.get("/by-area", response_model=list[AreaCount])
def insights_by_area(db: Session = Depends(get_db)):
    rows = (
        db.query(Insight.product_area, func.count(Insight.id).label("count"))
        .group_by(Insight.product_area)
        .order_by(func.count(Insight.id).desc())
        .all()
    )
    return [AreaCount(product_area=r[0], count=r[1]) for r in rows]


@router.get("/by-category", response_model=list[CategoryCount])
def insights_by_category(db: Session = Depends(get_db)):
    rows = (
        db.query(Insight.insight_category, func.count(Insight.id).label("count"))
        .group_by(Insight.insight_category)
        .order_by(func.count(Insight.id).desc())
        .all()
    )
    return [CategoryCount(insight_category=r[0], count=r[1]) for r in rows]


@router.get("/by-account", response_model=list[AccountCount])
def insights_by_account(db: Session = Depends(get_db)):
    rows = (
        db.query(Insight.account_name, func.count(Insight.id).label("count"))
        .group_by(Insight.account_name)
        .order_by(func.count(Insight.id).desc())
        .limit(20)
        .all()
    )
    return [AccountCount(account_name=r[0], count=r[1]) for r in rows]


@router.get("/trend", response_model=list[TrendPoint])
def insights_trend(db: Session = Depends(get_db)):
    rows = (
        db.query(
            func.to_char(func.date_trunc("week", Insight.date_of_record), "YYYY-MM-DD").label("week"),
            func.count(Insight.id).label("count"),
        )
        .group_by(func.date_trunc("week", Insight.date_of_record))
        .order_by(func.date_trunc("week", Insight.date_of_record))
        .all()
    )
    return [TrendPoint(week=r[0], count=r[1]) for r in rows]
