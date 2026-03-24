"""Pull call transcripts from Gong API.

Output: data/raw/gong.json
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

GONG_API_BASE = "https://api.gong.io/v2"
GONG_ACCESS_KEY = os.getenv("GONG_ACCESS_KEY", "")
GONG_ACCESS_KEY_SECRET = os.getenv("GONG_ACCESS_KEY_SECRET", "")
MAX_RESULTS = int(os.getenv("MAX_SIGNALS_PER_SOURCE", "50"))
MAX_TRANSCRIPT_CHARS = 15000  # ~4000 tokens, truncate long transcripts
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "raw" / "gong.json"


def _auth():
    return (GONG_ACCESS_KEY, GONG_ACCESS_KEY_SECRET)


def pull_calls(days_back: int = 30) -> list[dict]:
    """Pull recent Gong calls with transcripts."""
    if not GONG_ACCESS_KEY or not GONG_ACCESS_KEY_SECRET:
        log.error("GONG_ACCESS_KEY and GONG_ACCESS_KEY_SECRET must be set in .env")
        return []

    from_dt = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")
    to_dt = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # Step 1: List calls
    log.info(f"Listing Gong calls from {from_dt} to {to_dt}")
    list_url = f"{GONG_API_BASE}/calls"
    body = {
        "filter": {
            "fromDateTime": from_dt,
            "toDateTime": to_dt,
        },
        "cursor": None,
    }
    resp = requests.post(list_url, json=body, auth=_auth())
    resp.raise_for_status()
    calls_data = resp.json()
    call_ids = [c["id"] for c in calls_data.get("calls", [])][:MAX_RESULTS]
    log.info(f"Found {len(call_ids)} calls (capped at {MAX_RESULTS})")

    if not call_ids:
        return []

    # Step 2: Get transcripts
    log.info("Fetching transcripts...")
    transcript_url = f"{GONG_API_BASE}/calls/transcript"
    body = {"filter": {"callIds": call_ids}}
    resp = requests.post(transcript_url, json=body, auth=_auth())
    resp.raise_for_status()
    transcripts = {t["callId"]: t for t in resp.json().get("callTranscripts", [])}

    # Step 3: Build output
    signals = []
    for call in calls_data.get("calls", []):
        call_id = call["id"]
        transcript = transcripts.get(call_id, {})

        # Flatten transcript to text
        transcript_text = _flatten_transcript(transcript)
        if len(transcript_text) > MAX_TRANSCRIPT_CHARS:
            transcript_text = transcript_text[:MAX_TRANSCRIPT_CHARS] + "\n[TRUNCATED]"

        # Detect roles from participants
        participants = call.get("parties", [])
        roles = list({p.get("title", "Unknown") for p in participants if p.get("affiliation") == "INTERNAL"})

        signal = {
            "source_tool": "Gong",
            "source_type": "VoF",
            "source_link": call.get("url", f"https://app.gong.io/call?id={call_id}"),
            "account_name": _extract_account(call),
            "raw_content": transcript_text,
            "metadata": {
                "call_id": call_id,
                "title": call.get("title", ""),
                "started": call.get("started", ""),
                "duration_seconds": call.get("duration", 0),
                "direction": call.get("direction", ""),
                "roles_present": roles,
                "participant_count": len(participants),
            },
            "timestamp": call.get("started", ""),
        }
        signals.append(signal)

    log.info(f"Built {len(signals)} Gong signals")
    return signals


def _flatten_transcript(transcript: dict) -> str:
    """Flatten Gong transcript into readable text."""
    parts = []
    for segment in transcript.get("transcript", []):
        speaker = segment.get("speakerName", "Unknown")
        sentences = " ".join(s.get("text", "") for s in segment.get("sentences", []))
        if sentences.strip():
            parts.append(f"{speaker}: {sentences}")
    return "\n".join(parts)


def _extract_account(call: dict) -> str | None:
    """Try to extract account name from call metadata."""
    # Gong may have account info in the call context
    for party in call.get("parties", []):
        if party.get("affiliation") == "EXTERNAL":
            company = party.get("company", "")
            if company:
                return company
    return None


def main():
    signals = pull_calls()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(signals, indent=2, default=str))
    log.info(f"Wrote {len(signals)} signals to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
