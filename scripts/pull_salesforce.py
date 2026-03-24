"""Pull account data and Closed/Lost opportunity reasons from Salesforce.

Output: data/raw/salesforce.json (signals) and data/raw/sfdc_accounts.json (account reference list)
"""

import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from simple_salesforce import Salesforce

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

SF_USERNAME = os.getenv("SALESFORCE_USERNAME", "")
SF_PASSWORD = os.getenv("SALESFORCE_PASSWORD", "")
SF_SECURITY_TOKEN = os.getenv("SALESFORCE_SECURITY_TOKEN", "")
SF_DOMAIN = os.getenv("SALESFORCE_DOMAIN", "login")  # "login" or "test"
MAX_RESULTS = int(os.getenv("MAX_SIGNALS_PER_SOURCE", "50"))

OUTPUT_PATH = Path(__file__).parent.parent / "data" / "raw" / "salesforce.json"
ACCOUNTS_PATH = Path(__file__).parent.parent / "data" / "raw" / "sfdc_accounts.json"


def connect() -> Salesforce:
    if not SF_USERNAME or not SF_PASSWORD:
        raise ValueError("SALESFORCE_USERNAME and SALESFORCE_PASSWORD must be set in .env")
    return Salesforce(
        username=SF_USERNAME,
        password=SF_PASSWORD,
        security_token=SF_SECURITY_TOKEN,
        domain=SF_DOMAIN,
    )


def pull_accounts(sf: Salesforce) -> list[dict]:
    """Pull account reference data for enrichment and name matching."""
    log.info("Pulling SFDC account data...")
    query = """
        SELECT Id, Name, Industry, Type, AnnualRevenue, Description
        FROM Account
        WHERE Type != null
        ORDER BY Name
        LIMIT 500
    """
    result = sf.query_all(query)
    accounts = []
    for rec in result.get("records", []):
        accounts.append({
            "sfdc_account_id": rec["Id"],
            "account_name": rec["Name"],
            "vertical": rec.get("Industry", ""),
            "type": rec.get("Type", ""),
            "annual_revenue": rec.get("AnnualRevenue"),
            "description": rec.get("Description", ""),
        })
    log.info(f"Pulled {len(accounts)} accounts")
    return accounts


def pull_closed_lost(sf: Salesforce) -> list[dict]:
    """Pull Closed/Lost opportunities with loss reasons."""
    log.info("Pulling Closed/Lost opportunities...")
    query = f"""
        SELECT Id, Name, Account.Name, StageName, Amount,
               CloseDate, Loss_Reason__c, Description
        FROM Opportunity
        WHERE StageName = 'Closed Lost'
        AND CloseDate >= LAST_N_DAYS:90
        ORDER BY CloseDate DESC
        LIMIT {MAX_RESULTS}
    """
    try:
        result = sf.query_all(query)
    except Exception as e:
        # Loss_Reason__c may be a custom field with a different name
        log.warning(f"Query failed (custom field?): {e}. Trying without Loss_Reason__c...")
        query = f"""
            SELECT Id, Name, Account.Name, StageName, Amount,
                   CloseDate, Description
            FROM Opportunity
            WHERE StageName = 'Closed Lost'
            AND CloseDate >= LAST_N_DAYS:90
            ORDER BY CloseDate DESC
            LIMIT {MAX_RESULTS}
        """
        result = sf.query_all(query)

    signals = []
    for rec in result.get("records", []):
        account_name = rec.get("Account", {}).get("Name", "") if rec.get("Account") else ""
        loss_reason = rec.get("Loss_Reason__c", "") or ""
        description = rec.get("Description", "") or ""
        raw_content = f"Closed/Lost: {rec['Name']}\nAccount: {account_name}\nAmount: ${rec.get('Amount', 'N/A')}\nLoss Reason: {loss_reason}\nDescription: {description}"

        signals.append({
            "source_tool": "Salesforce",
            "source_type": "Loss",
            "source_link": f"https://coreweave.lightning.force.com/{rec['Id']}",
            "account_name": account_name or None,
            "raw_content": raw_content,
            "metadata": {
                "opportunity_name": rec["Name"],
                "stage": rec["StageName"],
                "amount": rec.get("Amount"),
                "close_date": rec.get("CloseDate", ""),
                "loss_reason": loss_reason,
            },
            "timestamp": rec.get("CloseDate", ""),
        })

    log.info(f"Pulled {len(signals)} Closed/Lost signals")
    return signals


def main():
    sf = connect()

    accounts = pull_accounts(sf)
    ACCOUNTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    ACCOUNTS_PATH.write_text(json.dumps(accounts, indent=2, default=str))
    log.info(f"Wrote {len(accounts)} accounts to {ACCOUNTS_PATH}")

    signals = pull_closed_lost(sf)
    OUTPUT_PATH.write_text(json.dumps(signals, indent=2, default=str))
    log.info(f"Wrote {len(signals)} signals to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
