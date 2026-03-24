"""Synthesize raw signals into structured insights using Claude API.

Reads from data/raw/*.json, calls Claude for extraction + classification,
applies dedup logic, outputs to data/output/insights.json and insights.csv.
"""

import csv
import json
import logging
import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "output"
PROMPTS_DIR = Path(__file__).parent.parent / "data" / "prompts"
ACCOUNTS_PATH = RAW_DIR / "sfdc_accounts.json"

# Insight CSV columns
CSV_COLUMNS = [
    "account_name",
    "insight_text",
    "product_area",
    "product_subcategory",
    "insight_category",
    "input_data_source",
    "source_tool",
    "source_link",
    "date_of_record",
    "unique_insight_status",
    "dedup_group_key",
]


def load_raw_signals() -> list[dict]:
    """Load all raw signals from data/raw/*.json."""
    all_signals = []
    source_files = list(RAW_DIR.glob("*.json"))
    # Exclude the SFDC accounts reference file
    source_files = [f for f in source_files if f.name != "sfdc_accounts.json"]

    for path in source_files:
        try:
            signals = json.loads(path.read_text())
            log.info(f"Loaded {len(signals)} signals from {path.name}")
            all_signals.extend(signals)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            log.warning(f"Failed to load {path}: {e}")

    log.info(f"Total raw signals: {len(all_signals)}")
    return all_signals


def load_account_names() -> list[str]:
    """Load SFDC account names for reference in Claude prompts."""
    if ACCOUNTS_PATH.exists():
        accounts = json.loads(ACCOUNTS_PATH.read_text())
        names = [a["account_name"] for a in accounts if a.get("account_name")]
        log.info(f"Loaded {len(names)} SFDC account names for matching")
        return names
    log.warning("No SFDC accounts file found — account matching will be best-effort")
    return []


def load_extraction_prompt() -> str:
    """Load the extraction prompt from data/prompts/extract.txt."""
    prompt_path = PROMPTS_DIR / "extract.txt"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Extraction prompt not found at {prompt_path}")
    return prompt_path.read_text()


def extract_insights(client: anthropic.Anthropic, signals: list[dict], system_prompt: str, account_names: list[str]) -> list[dict]:
    """Send signals to Claude for insight extraction."""
    all_insights = []

    # Add account name reference to system prompt if available
    if account_names:
        account_ref = "\n\n## SFDC Account Names (use these exact names for account_name):\n"
        account_ref += "\n".join(f"- {name}" for name in account_names[:200])  # Cap at 200
        full_system = system_prompt + account_ref
    else:
        full_system = system_prompt

    # Process signals in batches of 5 for efficiency
    batch_size = 5
    for i in range(0, len(signals), batch_size):
        batch = signals[i : i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(signals) + batch_size - 1) // batch_size
        log.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} signals)")

        # Build user message with all signals in the batch
        user_parts = []
        for j, signal in enumerate(batch):
            source_tool = signal.get("source_tool", "Unknown")
            source_type = signal.get("source_type", "Unknown")
            raw_content = signal.get("raw_content", "")
            user_parts.append(
                f"--- Signal {j + 1} (source: {source_tool}, type: {source_type}) ---\n{raw_content}"
            )

        user_message = "\n\n".join(user_parts)

        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=full_system,
                messages=[{"role": "user", "content": user_message}],
            )

            # Parse JSON from response
            response_text = response.content[0].text
            insights = _parse_json_response(response_text)

            # Enrich each insight with source metadata
            for insight in insights:
                # Find the most likely source signal for this insight
                matched_signal = _match_signal(insight, batch)
                insight["input_data_source"] = matched_signal.get("source_type", "")
                insight["source_tool"] = matched_signal.get("source_tool", "")
                insight["source_link"] = matched_signal.get("source_link", "")
                if not insight.get("date_of_record"):
                    insight["date_of_record"] = _extract_date(matched_signal)

            all_insights.extend(insights)
            log.info(f"  Extracted {len(insights)} insights from batch")

        except anthropic.APIError as e:
            log.error(f"  Claude API error on batch {batch_num}: {e}")
        except Exception as e:
            log.error(f"  Unexpected error on batch {batch_num}: {e}")

    log.info(f"Total insights extracted: {len(all_insights)}")
    return all_insights


def _parse_json_response(text: str) -> list[dict]:
    """Parse JSON from Claude's response, handling markdown fences and extra text."""
    # Try to find JSON array in the response
    # Pattern 1: ```json ... ```
    match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))

    # Pattern 2: Bare JSON array
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))

    log.warning(f"Could not parse JSON from response: {text[:200]}...")
    return []


def _match_signal(insight: dict, batch: list[dict]) -> dict:
    """Best-effort match an insight back to its source signal."""
    # If there's only one signal, it's obvious
    if len(batch) == 1:
        return batch[0]

    # Try matching by source_tool if present
    tool = insight.get("source_tool", "")
    if tool:
        for signal in batch:
            if signal.get("source_tool", "").lower() == tool.lower():
                return signal

    # Try matching by account name
    account = insight.get("account_name", "")
    if account:
        for signal in batch:
            if account.lower() in signal.get("raw_content", "").lower():
                return signal

    return batch[0]


def _extract_date(signal: dict) -> str:
    """Extract a date string from signal metadata."""
    ts = signal.get("timestamp", "")
    if ts:
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            pass
    # Fallback: today
    return datetime.now().strftime("%Y-%m-%d")


def apply_dedup(insights: list[dict]) -> list[dict]:
    """Apply deterministic deduplication logic.

    Group key: account_name | week_of(date) | product_area | product_subcategory | insight_category
    Rules:
    - Single row in group → Key Record
    - Multiple rows: prefer VoF source, then longest insight → Key Record, rest → Duplicate Record
    """
    log.info("Applying dedup logic...")

    # Compute group keys
    for insight in insights:
        date_str = insight.get("date_of_record", "")
        week = _week_of(date_str)
        account = (insight.get("account_name") or "unknown").lower().strip()
        area = insight.get("product_area", "").strip()
        sub = insight.get("product_subcategory", "").strip()
        cat = insight.get("insight_category", "").strip()
        insight["dedup_group_key"] = f"{account}|{week}|{area}|{sub}|{cat}"

    # Group insights
    groups: dict[str, list[dict]] = defaultdict(list)
    for insight in insights:
        groups[insight["dedup_group_key"]].append(insight)

    # Apply dedup rules
    key_count = 0
    dupe_count = 0
    for group_key, group in groups.items():
        if len(group) == 1:
            group[0]["unique_insight_status"] = "Key Record"
            key_count += 1
        else:
            # Find the key record
            key_record = _select_key_record(group)
            for insight in group:
                if insight is key_record:
                    insight["unique_insight_status"] = "Key Record"
                    key_count += 1
                else:
                    insight["unique_insight_status"] = "Duplicate Record"
                    dupe_count += 1

    log.info(f"Dedup result: {key_count} key records, {dupe_count} duplicates")
    return insights


def _week_of(date_str: str) -> str:
    """Return ISO week string for a date."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{dt.isocalendar()[0]}-W{dt.isocalendar()[1]:02d}"
    except (ValueError, TypeError):
        return "unknown-week"


def _select_key_record(group: list[dict]) -> dict:
    """Select the key record from a dedup group.

    Priority:
    1. VoF source
    2. Most detailed insight (longest by word count)
    """
    # Prefer VoF source
    vof_records = [i for i in group if i.get("input_data_source") == "VoF"]
    if vof_records:
        # Among VoF records, pick the longest
        return max(vof_records, key=lambda i: len(i.get("insight_text", "").split()))
    # No VoF: pick the longest
    return max(group, key=lambda i: len(i.get("insight_text", "").split()))


def write_output(insights: list[dict]):
    """Write insights to JSON and CSV."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # JSON
    json_path = OUTPUT_DIR / "insights.json"
    json_path.write_text(json.dumps(insights, indent=2, default=str))
    log.info(f"Wrote {len(insights)} insights to {json_path}")

    # CSV
    csv_path = OUTPUT_DIR / "insights.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(insights)
    log.info(f"Wrote {len(insights)} insights to {csv_path}")


def main():
    if not ANTHROPIC_API_KEY:
        log.error("ANTHROPIC_API_KEY must be set in .env")
        return

    # Load data
    signals = load_raw_signals()
    if not signals:
        log.error("No raw signals found in data/raw/. Run pull scripts first.")
        return

    account_names = load_account_names()
    system_prompt = load_extraction_prompt()

    # Extract insights via Claude
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    insights = extract_insights(client, signals, system_prompt, account_names)

    if not insights:
        log.error("No insights extracted. Check Claude API response.")
        return

    # Apply dedup
    insights = apply_dedup(insights)

    # Write output
    write_output(insights)

    # Print summary
    key_records = [i for i in insights if i.get("unique_insight_status") == "Key Record"]
    areas = defaultdict(int)
    for i in key_records:
        areas[i.get("product_area", "Unknown")] += 1

    log.info("=== Summary ===")
    log.info(f"Total signals processed: {len(signals)}")
    log.info(f"Total insights extracted: {len(insights)}")
    log.info(f"Key records: {len(key_records)}")
    log.info(f"Duplicates: {len(insights) - len(key_records)}")
    log.info("By product area:")
    for area, count in sorted(areas.items(), key=lambda x: -x[1]):
        log.info(f"  {area}: {count}")


if __name__ == "__main__":
    main()
