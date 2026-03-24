"""Pull survey responses from Qualtrics API.

Qualtrics exports are async: request export, poll, download.

Output: data/raw/qualtrics.json
"""

import json
import logging
import os
import time
import zipfile
from io import BytesIO
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

QUALTRICS_API_TOKEN = os.getenv("QUALTRICS_API_TOKEN", "")
QUALTRICS_DATACENTER = os.getenv("QUALTRICS_DATACENTER", "")  # e.g., "ca1", "iad1"
QUALTRICS_SURVEY_ID = os.getenv("QUALTRICS_SURVEY_ID", "")
MAX_RESULTS = int(os.getenv("MAX_SIGNALS_PER_SOURCE", "50"))
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "raw" / "qualtrics.json"


def _headers():
    return {
        "X-API-TOKEN": QUALTRICS_API_TOKEN,
        "Content-Type": "application/json",
    }


def _base_url():
    return f"https://{QUALTRICS_DATACENTER}.qualtrics.com/API/v3"


def pull_survey_responses() -> list[dict]:
    """Pull responses from a Qualtrics survey using the async export flow."""
    if not QUALTRICS_API_TOKEN or not QUALTRICS_DATACENTER or not QUALTRICS_SURVEY_ID:
        log.error("QUALTRICS_API_TOKEN, QUALTRICS_DATACENTER, and QUALTRICS_SURVEY_ID must be set in .env")
        return []

    base = _base_url()

    # Step 1: Start export
    log.info(f"Starting Qualtrics export for survey {QUALTRICS_SURVEY_ID}")
    export_url = f"{base}/surveys/{QUALTRICS_SURVEY_ID}/export-responses"
    resp = requests.post(export_url, json={"format": "json"}, headers=_headers())
    resp.raise_for_status()
    progress_id = resp.json()["result"]["progressId"]

    # Step 2: Poll for completion
    progress_url = f"{export_url}/{progress_id}"
    file_id = None
    for _ in range(30):  # Max 30 polls (30 seconds)
        resp = requests.get(progress_url, headers=_headers())
        resp.raise_for_status()
        result = resp.json()["result"]
        status = result["status"]
        if status == "complete":
            file_id = result["fileId"]
            break
        elif status == "failed":
            log.error("Qualtrics export failed")
            return []
        time.sleep(1)

    if not file_id:
        log.error("Qualtrics export timed out")
        return []

    # Step 3: Download
    log.info("Downloading Qualtrics export...")
    download_url = f"{export_url}/{file_id}/file"
    resp = requests.get(download_url, headers=_headers())
    resp.raise_for_status()

    # Response is a ZIP containing a JSON file
    with zipfile.ZipFile(BytesIO(resp.content)) as zf:
        json_filename = zf.namelist()[0]
        with zf.open(json_filename) as f:
            survey_data = json.load(f)

    responses = survey_data.get("responses", [])[:MAX_RESULTS]
    log.info(f"Downloaded {len(responses)} responses")

    # Step 4: Convert to signals
    signals = []
    for response in responses:
        values = response.get("values", {})
        displayed = response.get("displayedValues", {})

        # Build a readable text from all question/answer pairs
        qa_parts = []
        for key, value in displayed.items():
            if key.startswith("Q") and value:
                qa_parts.append(f"{key}: {value}")

        raw_content = "\n".join(qa_parts) if qa_parts else json.dumps(displayed)

        signal = {
            "source_tool": "Qualtrics",
            "source_type": "Survey",
            "source_link": f"https://{QUALTRICS_DATACENTER}.qualtrics.com/responses/{QUALTRICS_SURVEY_ID}",
            "account_name": None,  # Extracted by Claude or from survey field
            "raw_content": raw_content,
            "metadata": {
                "response_id": response.get("responseId", ""),
                "survey_id": QUALTRICS_SURVEY_ID,
                "recorded_date": values.get("recordedDate", ""),
                "duration_seconds": values.get("duration", 0),
            },
            "timestamp": values.get("recordedDate", ""),
        }
        signals.append(signal)

    log.info(f"Built {len(signals)} Qualtrics signals")
    return signals


def main():
    signals = pull_survey_responses()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(signals, indent=2, default=str))
    log.info(f"Wrote {len(signals)} signals to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
