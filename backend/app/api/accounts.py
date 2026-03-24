from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.insight import Insight
from app.schemas.insight import InsightResponse

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.get("")
def list_accounts(
    q: Optional[str] = Query(None, description="Search account name"),
    db: Session = Depends(get_db),
):
    query = (
        db.query(
            Insight.account_name,
            func.count(Insight.id).label("insight_count"),
        )
        .group_by(Insight.account_name)
    )
    if q:
        query = query.filter(Insight.account_name.ilike(f"%{q}%"))
    rows = query.order_by(func.count(Insight.id).desc()).all()
    return [{"account_name": r[0], "insight_count": r[1]} for r in rows]


@router.get("/{account_name}")
def get_account(account_name: str, db: Session = Depends(get_db)):
    insights = (
        db.query(Insight)
        .filter(Insight.account_name == account_name)
        .order_by(Insight.date_of_record.desc())
        .all()
    )
    if not insights:
        raise HTTPException(status_code=404, detail="Account not found or has no insights")
    return {
        "account_name": account_name,
        "insight_count": len(insights),
        "insights": [InsightResponse.model_validate(i) for i in insights],
    }
