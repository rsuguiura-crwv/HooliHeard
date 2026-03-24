"""Pull customer feedback messages from designated Slack channels.

Collapses threads into single signals.

Output: data/raw/slack.json
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_CHANNELS = os.getenv("SLACK_CHANNELS", "")  # comma-separated channel IDs
MAX_RESULTS = int(os.getenv("MAX_SIGNALS_PER_SOURCE", "50"))
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "raw" / "slack.json"


def pull_messages(days_back: int = 30) -> list[dict]:
    """Pull messages from designated Slack channels."""
    if not SLACK_BOT_TOKEN:
        log.error("SLACK_BOT_TOKEN must be set in .env")
        return []

    if not SLACK_CHANNELS:
        log.error("SLACK_CHANNELS must be set in .env (comma-separated channel IDs)")
        return []

    client = WebClient(token=SLACK_BOT_TOKEN)
    channel_ids = [c.strip() for c in SLACK_CHANNELS.split(",") if c.strip()]
    oldest = str((datetime.now() - timedelta(days=days_back)).timestamp())

    all_signals = []

    for channel_id in channel_ids:
        log.info(f"Pulling messages from channel {channel_id}")
        try:
            # Get channel info for name
            channel_info = client.conversations_info(channel=channel_id)
            channel_name = channel_info["channel"]["name"]
        except SlackApiError as e:
            log.warning(f"Could not get channel info for {channel_id}: {e}")
            channel_name = channel_id

        try:
            result = client.conversations_history(
                channel=channel_id,
                oldest=oldest,
                limit=MAX_RESULTS,
            )
        except SlackApiError as e:
            log.error(f"Failed to pull messages from {channel_id}: {e}")
            continue

        messages = result.get("messages", [])
        log.info(f"Found {len(messages)} messages in #{channel_name}")

        for msg in messages:
            # Skip bot messages and join/leave messages
            if msg.get("subtype") in ("bot_message", "channel_join", "channel_leave"):
                continue

            text = msg.get("text", "")
            if not text.strip():
                continue

            # If message has a thread, fetch replies and collapse
            thread_ts = msg.get("thread_ts")
            if thread_ts and thread_ts == msg.get("ts"):
                thread_text = _fetch_thread(client, channel_id, thread_ts)
                if thread_text:
                    text = thread_text

            ts = float(msg.get("ts", 0))
            timestamp = datetime.fromtimestamp(ts).isoformat() if ts else ""

            signal = {
                "source_tool": "Slack",
                "source_type": "CX",
                "source_link": f"https://coreweave.slack.com/archives/{channel_id}/p{msg.get('ts', '').replace('.', '')}",
                "account_name": None,  # Will be extracted by Claude
                "raw_content": text,
                "metadata": {
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "thread_ts": thread_ts,
                    "user": msg.get("user", ""),
                    "has_thread": thread_ts is not None,
                },
                "timestamp": timestamp,
            }
            all_signals.append(signal)

    log.info(f"Total: {len(all_signals)} Slack signals")
    return all_signals


def _fetch_thread(client: WebClient, channel_id: str, thread_ts: str) -> str | None:
    """Fetch and collapse thread replies into a single text block."""
    try:
        result = client.conversations_replies(
            channel=channel_id,
            ts=thread_ts,
            limit=50,
        )
        messages = result.get("messages", [])
        if len(messages) <= 1:
            return None

        parts = []
        for msg in messages:
            user = msg.get("user", "Unknown")
            text = msg.get("text", "")
            if text.strip():
                parts.append(f"{user}: {text}")
        return "\n".join(parts)
    except SlackApiError as e:
        log.warning(f"Failed to fetch thread {thread_ts}: {e}")
        return None


def main():
    signals = pull_messages()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(signals, indent=2, default=str))
    log.info(f"Wrote {len(signals)} signals to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
