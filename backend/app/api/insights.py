import csv
import io
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.insight import Insight
from app.schemas.insight import InsightListResponse, InsightResponse

router = APIRouter(prefix="/api/insights", tags=["insights"])


def _apply_filters(query, product_area, insight_category, account_name, date_from, date_to, unique_insight_status):
    if product_area:
        query = query.filter(Insight.product_area == product_area)
    if insight_category:
        query = query.filter(Insight.insight_category == insight_category)
    if account_name:
        query = query.filter(Insight.account_name.ilike(f"%{account_name}%"))
    if date_from:
        query = query.filter(Insight.date_of_record >= date_from)
    if date_to:
        query = query.filter(Insight.date_of_record <= date_to)
    if unique_insight_status:
        query = query.filter(Insight.unique_insight_status == unique_insight_status)
    return query


@router.get("/export")
def export_insights_csv(
    product_area: Optional[str] = Query(None),
    insight_category: Optional[str] = Query(None),
    account_name: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    unique_insight_status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Insight)
    q = _apply_filters(q, product_area, insight_category, account_name, date_from, date_to, unique_insight_status)
    rows = q.order_by(Insight.date_of_record.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "account_name", "insight_text", "product_area", "product_subcategory",
        "insight_category", "source_tool", "source_link", "date_of_record",
        "unique_insight_status", "comments",
    ])
    for r in rows:
        writer.writerow([
            str(r.id), r.account_name, r.insight_text, r.product_area,
            r.product_subcategory, r.insight_category, r.source_tool,
            r.source_link, str(r.date_of_record), r.unique_insight_status,
            r.comments,
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=insights_export.csv"},
    )


@router.get("/{insight_id}", response_model=InsightResponse)
def get_insight(insight_id: UUID, db: Session = Depends(get_db)):
    row = db.query(Insight).filter(Insight.id == insight_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Insight not found")
    return row


@router.get("", response_model=InsightListResponse)
def list_insights(
    product_area: Optional[str] = Query(None),
    insight_category: Optional[str] = Query(None),
    account_name: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    unique_insight_status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(Insight)
    q = _apply_filters(q, product_area, insight_category, account_name, date_from, date_to, unique_insight_status)

    total = q.count()
    rows = q.order_by(Insight.date_of_record.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return InsightListResponse(items=rows, total=total, page=page, page_size=page_size)
