"""Pull Customer Feature Requests from the CFR Jira project.

ONLY pulls from https://coreweave.atlassian.net/jira/software/c/projects/CFR/list
No support tickets (TSM-, SR-).

Output: data/raw/jira_cfr.json
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "https://coreweave.atlassian.net")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
MAX_RESULTS = int(os.getenv("MAX_SIGNALS_PER_SOURCE", "50"))
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "raw" / "jira_cfr.json"


def pull_cfr_tickets(days_back: int = 90) -> list[dict]:
    """Pull CFR tickets from the last N days."""
    if not JIRA_EMAIL or not JIRA_API_TOKEN:
        log.error("JIRA_EMAIL and JIRA_API_TOKEN must be set in .env")
        return []

    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    since = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    jql = f'project = CFR AND created >= "{since}" ORDER BY key DESC'
    url = f"{JIRA_BASE_URL}/rest/api/3/search"
    params = {
        "jql": jql,
        "maxResults": MAX_RESULTS,
        "fields": "summary,description,created,updated,status,priority,labels,customfield_*,components,issuetype",
    }

    log.info(f"Pulling CFR tickets since {since} (max {MAX_RESULTS})")
    resp = requests.get(url, auth=auth, params=params)
    resp.raise_for_status()
    data = resp.json()

    tickets = []
    for issue in data.get("issues", []):
        key = issue["key"]
        # Double-check: only CFR- prefixed keys
        if not key.startswith("CFR-"):
            continue

        fields = issue["fields"]

        # Extract description text from Atlassian Document Format
        description_text = ""
        if fields.get("description"):
            description_text = _extract_adf_text(fields["description"])

        ticket = {
            "source_tool": "Jira",
            "source_type": "CX",
            "source_link": f"{JIRA_BASE_URL}/browse/{key}",
            "ticket_key": key,
            "summary": fields.get("summary", ""),
            "description": description_text,
            "status": fields.get("status", {}).get("name", ""),
            "priority": fields.get("priority", {}).get("name", ""),
            "components": [c.get("name", "") for c in fields.get("components", [])],
            "labels": fields.get("labels", []),
            "created": fields.get("created", ""),
            "updated": fields.get("updated", ""),
            "raw_content": f"CFR Ticket {key}: {fields.get('summary', '')}\n\n{description_text}",
            "metadata": {
                "issue_type": fields.get("issuetype", {}).get("name", ""),
                "components": [c.get("name", "") for c in fields.get("components", [])],
            },
        }
        tickets.append(ticket)

    log.info(f"Pulled {len(tickets)} CFR tickets")
    return tickets


def _extract_adf_text(adf: dict) -> str:
    """Recursively extract plain text from Atlassian Document Format."""
    if isinstance(adf, str):
        return adf
    if not isinstance(adf, dict):
        return ""

    text_parts = []
    if adf.get("type") == "text":
        text_parts.append(adf.get("text", ""))

    for child in adf.get("content", []):
        text_parts.append(_extract_adf_text(child))

    return " ".join(text_parts).strip()


def main():
    tickets = pull_cfr_tickets()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(tickets, indent=2, default=str))
    log.info(f"Wrote {len(tickets)} tickets to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
