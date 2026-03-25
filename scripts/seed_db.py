#!/usr/bin/env python3
"""Seed the database with insights from data/output/insights.json or generate sample data."""

import json
import sys
import uuid
from datetime import date, datetime, timezone
from pathlib import Path

# Allow running from repo root or scripts/
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app.config import settings  # noqa: E402
from app.db import engine, SessionLocal, create_all  # noqa: E402
from app.models.insight import Insight  # noqa: E402

# Check multiple paths: repo root (local dev), /data (docker-compose mount), cwd (k8s seed image)
INSIGHTS_JSON = ROOT / "data" / "output" / "insights.json"
if not INSIGHTS_JSON.exists():
    INSIGHTS_JSON = Path("/data/output/insights.json")
if not INSIGHTS_JSON.exists():
    INSIGHTS_JSON = Path("insights.json")

# ---------------------------------------------------------------------------
# Sample data generator
# ---------------------------------------------------------------------------

PRODUCT_AREAS = ["Infra", "CKS", "Platform", "AI Services", "W&B"]
SUBCATEGORIES = {
    "Infra": ["Compute", "Storage", "Networking"],
    "CKS": ["BMaaS", "CKS", "Consumption Models"],
    "Platform": ["Security & Compliance", "Console / API / Terraform", "Observability"],
    "AI Services": ["SUNK / Training", "Inference", "RL / Evals"],
    "W&B": ["n/a"],
}
CATEGORIES = [
    "Capacity", "Capacity Issues", "Pricing / Terms",
    "Customer Requirements (Enhancement)", "Customer Requirements (Blocker)",
    "Issues", "Education Gaps", "Competition / Alternatives",
    "Success Pattern / Win Signal", "Process / Operational Friction",
]
SOURCES = ["Gong", "Salesforce", "Jira", "Slack", "Qualtrics"]
SOURCE_TYPES = {"Gong": "VoF", "Salesforce": "Loss", "Jira": "CX", "Slack": "CX", "Qualtrics": "Survey"}
ACCOUNTS = [
    "Anthropic", "Meta", "Microsoft", "Mistral AI", "Cohere",
    "Databricks", "Scale AI", "Hugging Face", "Stability AI", "Perplexity",
]
ROLES = ["AE", "SA", "TSM", "CX", None]
CONV_TYPES = ["AE", "SA", "TSM"]

SAMPLE_INSIGHTS = [
    ("Infra", "Compute", "Capacity", "Customer needs 512 H100s in ORD1 by end of Q2 for large-scale training run"),
    ("Infra", "Compute", "Capacity Issues", "Reserved H100 instances in LGA1 unavailable for 3 consecutive weeks"),
    ("Infra", "Networking", "Customer Requirements (Enhancement)", "Need 400Gbps InfiniBand for multi-node training across racks"),
    ("Infra", "Storage", "Issues", "IOPS throttling on block storage during checkpoint writes causes job failures"),
    ("Infra", "Compute", "Competition / Alternatives", "Customer evaluating Lambda Labs due to H200 availability gap"),
    ("CKS", "CKS", "Customer Requirements (Enhancement)", "Need HPA support for custom GPU metrics to autoscale inference pods"),
    ("CKS", "CKS", "Issues", "Cluster upgrades cause 5-10 min downtime for running inference workloads"),
    ("CKS", "BMaaS", "Customer Requirements (Blocker)", "Bare metal access required for custom CUDA driver versions — blocking expansion"),
    ("CKS", "Consumption Models", "Pricing / Terms", "Need committed-use discount structure for 1-year GPU reservations"),
    ("CKS", "CKS", "Education Gaps", "Customer confused about node pool configuration for mixed GPU types"),
    ("Platform", "Console / API / Terraform", "Customer Requirements (Enhancement)", "Terraform provider missing support for CKS node pool configuration"),
    ("Platform", "Security & Compliance", "Customer Requirements (Blocker)", "SOC2 Type II audit logs required for API access — blocking security review"),
    ("Platform", "Observability", "Customer Requirements (Enhancement)", "Need capacity alerts when reserved instances are running low"),
    ("Platform", "Console / API / Terraform", "Issues", "Console returns 500 error when creating clusters with 100+ nodes"),
    ("Platform", "Security & Compliance", "Process / Operational Friction", "IAM role provisioning takes 3+ days through manual process"),
    ("AI Services", "Inference", "Customer Requirements (Enhancement)", "Need built-in A/B testing for model serving endpoints"),
    ("AI Services", "Inference", "Issues", "Cold start times for serverless inference endpoints exceed 30s SLA"),
    ("AI Services", "SUNK / Training", "Success Pattern / Win Signal", "Training 70B model was seamless — customer expanding from 256 to 1024 GPUs"),
    ("AI Services", "Inference", "Competition / Alternatives", "Customer comparing CW inference latency against Anyscale and Modal"),
    ("AI Services", "RL / Evals", "Customer Requirements (Enhancement)", "Need integrated eval framework for RLHF pipeline on CW infrastructure"),
    ("W&B", "n/a", "Customer Requirements (Enhancement)", "Want W&B experiment tracking deeply integrated with CW training jobs"),
    ("Infra", "Compute", "Pricing / Terms", "Customer requesting spot instance pricing for non-critical batch workloads"),
    ("CKS", "CKS", "Success Pattern / Win Signal", "New cluster dashboard significantly reduced customer onboarding time"),
    ("Platform", "Observability", "Education Gaps", "Customer unaware of existing Prometheus metrics endpoint for GPU monitoring"),
    ("AI Services", "Inference", "Capacity Issues", "GPU availability for A100-80GB in LGA1 has been inconsistent for production inference"),
    ("Infra", "Networking", "Success Pattern / Win Signal", "200Gbps node-to-node throughput excellent for distributed training workloads"),
    ("Platform", "Console / API / Terraform", "Customer Requirements (Enhancement)", "Need API rate limit increase for automated cluster management scripts"),
    ("AI Services", "SUNK / Training", "Customer Requirements (Blocker)", "Multi-node training requires manual NCCL configuration — blocking adoption"),
    ("CKS", "Consumption Models", "Competition / Alternatives", "Customer evaluating AWS Trainium due to more flexible commitment terms"),
    ("Infra", "Storage", "Customer Requirements (Enhancement)", "Need NVMe-backed storage tier for database workloads alongside GPU compute"),
]


def generate_sample_insights() -> list[dict]:
    insights = []
    for i, (area, subcat, category, text) in enumerate(SAMPLE_INSIGHTS):
        account = ACCOUNTS[i % len(ACCOUNTS)]
        source = SOURCES[i % len(SOURCES)]
        role = ROLES[i % len(ROLES)]
        conv = CONV_TYPES[i % len(CONV_TYPES)]
        day = 1 + (i % 28)
        month = 1 + (i % 3)
        insights.append({
            "account_name": account,
            "insight_text": text,
            "product_area": area,
            "product_subcategory": subcat,
            "insight_category": category,
            "input_data_source": source,
            "source_tool": source,
            "source_link": f"https://example.com/{source}/{i+1}",
            "role_present": role,
            "conversation_type": conv,
            "date_of_record": f"2026-{month:02d}-{day:02d}",
            "comments": None,
            "dedup_group_key": f"{area}|{subcat}|{account}|{text[:50]}",
            "unique_insight_status": "Key Record",
        })
    return insights


STAGE_WEIGHTS = {
    "Closed Won": 10, "Negotiation": 8, "Proposal": 7, "Capacity Review": 6,
    "Discovery": 3, "Prospecting": 2, "New": 1,
}

CATEGORY_URGENCY = {
    "Customer Requirements (Blocker)": 10, "Capacity Issues": 8, "Issues": 7,
    "Process / Operational Friction": 6, "Customer Requirements (Enhancement)": 5,
    "Capacity": 5, "Competition / Alternatives": 5, "Pricing / Terms": 4,
    "Education Gaps": 3, "Success Pattern / Win Signal": 2, "GTM / Partnership": 2,
    "Product Fit / Scope": 2, "Null": 1,
}

TIER_MULTIPLIERS = {
    "Top Account": 3.0, "Strategic": 3.0, "Growth": 2.0, "Standard": 1.0,
}


def compute_priority_score(row):
    """Compute a RICE-inspired priority score from account enrichment data.

    Uses log-scale for opportunity amount to differentiate across wide ranges
    ($10K to $10M+). Scores range roughly from 0.1 to ~50 for top-priority items.
    """
    import math

    opp = row.get("opportunity_amount") or 0
    # Log-scale: $1K→1, $10K→2.3, $100K→3.5, $1M→4.6, $10M→5.8, capped at 10
    opp_score = min(10, max(1, math.log10(max(opp, 1)) - 2)) if opp > 0 else 1

    stage = row.get("opportunity_stage") or ""
    stage_score = STAGE_WEIGHTS.get(stage, 3)

    revenue = row.get("total_revenue") or 0
    won_count = row.get("closed_won_opp_count") or 0
    engagement_score = min(10, 1 + (math.log10(max(revenue, 1)) - 2 if revenue > 100 else 0) + won_count * 0.5)

    cat = row.get("insight_category") or ""
    cat_score = CATEGORY_URGENCY.get(cat, 3)

    tier = row.get("account_priority_group") or "Standard"
    multiplier = TIER_MULTIPLIERS.get(tier, 1.0)

    raw = (opp_score * stage_score * engagement_score * cat_score * multiplier) / 100
    return round(raw, 2)


def compute_urgency_level(row):
    cat = row.get("insight_category") or ""
    score = CATEGORY_URGENCY.get(cat, 3)
    if score >= 8:
        return "High"
    elif score >= 5:
        return "Medium"
    return "Low"


def load_insights(data: list[dict], session) -> int:
    count = 0
    for row in data:
        priority = compute_priority_score(row)
        urgency = compute_urgency_level(row)
        insight = Insight(
            id=uuid.uuid4(),
            account_name=row.get("account_name") or "Unknown",
            insight_text=row["insight_text"],
            product_area=row["product_area"],
            product_subcategory=row.get("product_subcategory", "General"),
            insight_category=row["insight_category"],
            input_data_source=row.get("input_data_source"),
            source_tool=row.get("source_tool", "unknown"),
            source_link=row.get("source_link"),
            role_present=row.get("role_present"),
            conversation_type=row.get("conversation_type"),
            date_of_record=date.fromisoformat(row["date_of_record"]) if isinstance(row["date_of_record"], str) else row["date_of_record"],
            comments=row.get("comments"),
            dedup_group_key=row.get("dedup_group_key"),
            unique_insight_status=row.get("unique_insight_status", "Key Record"),
            # V2 account enrichment
            icp=row.get("icp"),
            account_priority_group=row.get("account_priority_group"),
            vertical=row.get("vertical"),
            use_case=row.get("use_case"),
            workloads=row.get("workloads"),
            opportunity_stage=row.get("opportunity_stage"),
            opportunity_amount=row.get("opportunity_amount"),
            gpu_types=row.get("gpu_types"),
            competitors_mentioned=row.get("competitors_mentioned"),
            total_revenue=row.get("total_revenue"),
            most_recent_revenue_month=row.get("most_recent_revenue_month"),
            closed_won_opp_count=row.get("closed_won_opp_count"),
            # Computed
            priority_score=priority,
            urgency_level=urgency,
        )
        session.add(insight)
        count += 1
    session.commit()
    return count


def main():
    print("Creating tables...")
    create_all()

    session = SessionLocal()
    try:
        existing = session.query(Insight).count()
        if existing > 0:
            print(f"Database has {existing} insights. Clearing for re-seed...")
            session.query(Insight).delete()
            session.commit()

        if INSIGHTS_JSON.exists():
            print(f"Loading insights from {INSIGHTS_JSON}")
            with open(INSIGHTS_JSON) as f:
                data = json.load(f)
            if isinstance(data, dict) and "insights" in data:
                data = data["insights"]
        else:
            print("insights.json not found, generating sample data...")
            data = generate_sample_insights()

        count = load_insights(data, session)
        print(f"Seeded {count} insights into the database.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
