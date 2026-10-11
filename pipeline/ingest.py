"""Bronze layer: save raw API responses exactly as received."""
import json
from pathlib import Path

import requests

API = "https://clinicaltrials.gov/api/v2/studies"
CONDITIONS = ["type 2 diabetes", "breast cancer", "alzheimer disease"]


def fetch(condition, limit=100, page_size=50):
    """Follow nextPageToken until we have `limit` recruiting trials."""
    studies, token = [], None
    while len(studies) < limit:
        params = {
            "query.cond": condition,
            "filter.overallStatus": "RECRUITING",
            "sort": "LastUpdatePostDate:desc",
            "pageSize": page_size,
        }
        if token:
            params["pageToken"] = token
        response = requests.get(API, params=params, timeout=30)
        response.raise_for_status()
        page = response.json()
        studies += page["studies"]
        token = page.get("nextPageToken")
        if not token:
            break
    return studies[:limit]


def run(bronze_dir, limit=100):
    """One file per condition, overwritten each run, so re-running is safe."""
    bronze_dir = Path(bronze_dir)
    bronze_dir.mkdir(parents=True, exist_ok=True)
    for condition in CONDITIONS:
        path = bronze_dir / (condition.replace(" ", "_") + ".json")
        path.write_text(json.dumps(fetch(condition, limit)))
