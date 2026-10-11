"""Silver layer: one clean, typed row per trial."""
import json
from pathlib import Path

import pandas as pd


def flatten(study):
    """Pick the fields we need out of the nested API record."""
    p = study["protocolSection"]
    status = p.get("statusModule", {})
    design = p.get("designModule", {})
    sponsor = p.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {})
    interventions = p.get("armsInterventionsModule", {}).get("interventions", [])
    return {
        "nct_id": p["identificationModule"]["nctId"],
        "title": p["identificationModule"].get("briefTitle"),
        "phase": "/".join(design.get("phases", [])) or "NA",
        "status": status.get("overallStatus"),
        "enrollment": design.get("enrollmentInfo", {}).get("count"),
        "start_date": status.get("startDateStruct", {}).get("date"),
        "last_update": status.get("lastUpdatePostDateStruct", {}).get("date"),
        "sponsor_name": sponsor.get("name", "Unknown"),
        "sponsor_class": sponsor.get("class", "UNKNOWN"),
        "conditions": p.get("conditionsModule", {}).get("conditions", []),
        "interventions": [f"{i.get('type', 'OTHER')}: {i.get('name', '')}" for i in interventions],
        "summary": p.get("descriptionModule", {}).get("briefSummary", ""),
        "criteria": p.get("eligibilityModule", {}).get("eligibilityCriteria", ""),
    }


def run(con, bronze_dir):
    files = sorted(Path(bronze_dir).glob("*.json"))
    rows = [flatten(study) for f in files for study in json.loads(f.read_text())]
    con.register("raw_trial", pd.DataFrame(rows))
    # A trial can match several conditions, so keep one row per nct_id.
    # Some dates come as YYYY-MM; pad them so they cast to DATE.
    con.execute("""
        CREATE OR REPLACE TABLE silver_trial AS
        SELECT nct_id, title, phase, status,
               CAST(enrollment AS INTEGER) AS enrollment,
               TRY_CAST(CASE WHEN length(start_date) = 7 THEN start_date || '-01'
                             ELSE start_date END AS DATE) AS start_date,
               sponsor_name, sponsor_class, conditions, interventions, summary, criteria
        FROM raw_trial
        QUALIFY row_number() OVER (PARTITION BY nct_id ORDER BY last_update DESC) = 1
    """)
