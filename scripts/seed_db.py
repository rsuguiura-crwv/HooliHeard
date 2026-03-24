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

INSIGHTS_JSON = ROOT / "data" / "output" / "insights.json"

# ---------------------------------------------------------------------------
# Sample data generator
# ---------------------------------------------------------------------------

PRODUCT_AREAS = ["Kubernetes", "Networking", "Storage", "Inference", "HPC"]
SUBCATEGORIES = {
    "Kubernetes": ["Cluster Management", "Autoscaling", "Node Pools"],
    "Networking": ["Load Balancing", "VPC Peering", "Bandwidth"],
    "Storage": ["Block Storage", "Object Storage", "Snapshots"],
    "Inference": ["Model Serving", "Batch Inference", "GPU Scheduling"],
    "HPC": ["Job Scheduling", "MPI Support", "Large-scale Training"],
}
CATEGORIES = ["Feature Request", "Pain Point", "Churn Risk", "Praise", "Bug Report"]
SOURCES = ["gong", "salesforce", "jira", "slack", "qualtrics"]
ACCOUNTS = [
    "Acme Corp", "Globex Inc", "Initech", "Umbrella Corp", "Stark Industries",
    "Wayne Enterprises", "Cyberdyne Systems", "Soylent Corp", "Tyrell Corp", "Aperture Science",
]
ROLES = ["CTO", "VP Engineering", "ML Engineer", "DevOps Lead", "Platform Engineer"]
CONV_TYPES = ["Discovery Call", "QBR", "Support Ticket", "Survey Response", "Slack Thread"]

SAMPLE_INSIGHTS = [
    ("Kubernetes", "Autoscaling", "Feature Request", "Need HPA support for custom GPU metrics to autoscale inference workloads"),
    ("Kubernetes", "Cluster Management", "Pain Point", "Cluster upgrades cause 5-10 min downtime for running pods"),
    ("Kubernetes", "Node Pools", "Feature Request", "Want mixed GPU node pools with spot instance support"),
    ("Networking", "Load Balancing", "Bug Report", "L7 load balancer drops WebSocket connections after 60s idle"),
    ("Networking", "VPC Peering", "Pain Point", "Cross-region VPC peering latency is 3x higher than expected"),
    ("Networking", "Bandwidth", "Feature Request", "Need 400Gbps InfiniBand option for large training jobs"),
    ("Storage", "Block Storage", "Pain Point", "IOPS throttling on block storage during checkpoint writes"),
    ("Storage", "Object Storage", "Feature Request", "S3-compatible object storage needs versioning support"),
    ("Storage", "Snapshots", "Praise", "Snapshot restore is incredibly fast, saved us during an incident"),
    ("Inference", "Model Serving", "Feature Request", "Need built-in A/B testing for model endpoints"),
    ("Inference", "Batch Inference", "Pain Point", "Batch inference jobs fail silently when GPU OOM occurs"),
    ("Inference", "GPU Scheduling", "Churn Risk", "Considering alternatives due to GPU availability SLA misses"),
    ("Inference", "Model Serving", "Feature Request", "Want streaming response support for LLM serving endpoints"),
    ("Inference", "GPU Scheduling", "Pain Point", "H100 availability in ORD1 has been inconsistent for 3 weeks"),
    ("HPC", "Job Scheduling", "Feature Request", "Need priority queues for different teams within same org"),
    ("HPC", "MPI Support", "Bug Report", "MPI all-reduce fails intermittently on 256+ node jobs"),
    ("HPC", "Large-scale Training", "Praise", "Training a 70B model was seamless on the platform"),
    ("HPC", "Job Scheduling", "Pain Point", "No way to preempt low-priority jobs when urgent work comes in"),
    ("Kubernetes", "Autoscaling", "Churn Risk", "If autoscaling doesn't improve by Q2 we will evaluate other providers"),
    ("Storage", "Block Storage", "Feature Request", "Need NVMe-backed block storage tier for database workloads"),
    ("Networking", "Load Balancing", "Feature Request", "Want gRPC health check support on load balancers"),
    ("Inference", "Batch Inference", "Feature Request", "Need spot GPU support for cost-effective batch inference"),
    ("Kubernetes", "Cluster Management", "Praise", "The new cluster dashboard is a huge improvement"),
    ("HPC", "Large-scale Training", "Pain Point", "Checkpoint storage costs are too high for multi-day training runs"),
    ("Storage", "Object Storage", "Bug Report", "Multipart upload fails for files over 50GB"),
    ("Networking", "Bandwidth", "Praise", "200Gbps throughput between nodes is excellent for our distributed training"),
    ("Inference", "Model Serving", "Pain Point", "Cold start times for serverless inference are too high for production"),
    ("Kubernetes", "Node Pools", "Bug Report", "Taint propagation is broken when adding nodes to existing pool"),
    ("HPC", "MPI Support", "Feature Request", "Need NCCL 2.19 support for better multi-node communication"),
    ("Storage", "Snapshots", "Feature Request", "Want scheduled automatic snapshots with retention policies"),
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


def load_insights(data: list[dict], session) -> int:
    count = 0
    for row in data:
        insight = Insight(
            id=uuid.uuid4(),
            account_name=row["account_name"],
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
            print(f"Database already has {existing} insights. Skipping seed.")
            print("To re-seed, truncate the insights table first.")
            return

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
