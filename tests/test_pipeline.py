"""Data quality checks on a tiny hand-made bronze layer (no network, no model)."""
import json

import duckdb
import pytest

from pipeline import chunk_embed, model, transform
from pipeline.search import search


def study(nct_id, sponsor, conditions, criteria, start="2024-01"):
    return {"protocolSection": {
        "identificationModule": {"nctId": nct_id, "briefTitle": f"Trial {nct_id}"},
        "statusModule": {"overallStatus": "RECRUITING", "startDateStruct": {"date": start}},
        "designModule": {"phases": ["PHASE2"], "enrollmentInfo": {"count": 40}},
        "sponsorCollaboratorsModule": {"leadSponsor": {"name": sponsor, "class": "INDUSTRY"}},
        "conditionsModule": {"conditions": conditions},
        "armsInterventionsModule": {"interventions": [{"type": "DRUG", "name": "Metformin"}]},
        "descriptionModule": {"briefSummary": "A short summary."},
        "eligibilityModule": {"eligibilityCriteria": criteria},
    }}


def fake_embed(texts):
    return [[float(len(t))] + [0.0] * 383 for t in texts]


@pytest.fixture
def con(tmp_path):
    a = study("NCT1", "Acme", ["Type 2 Diabetes"], "Inclusion Criteria:\n* Adult\n\nExclusion Criteria:\n* Pregnant")
    b = study("NCT2", "Acme", ["Breast Cancer", "type 2 diabetes "], "Adults only", start="2023-05-17")
    c = study("NCT3", "Beta", ["Alzheimer Disease"], "")
    (tmp_path / "one.json").write_text(json.dumps([a, b]))
    (tmp_path / "two.json").write_text(json.dumps([b, c]))  # NCT2 appears twice
    con = duckdb.connect()
    transform.run(con, tmp_path)
    model.run(con)
    chunk_embed.run(con, embed=fake_embed)
    return con


def count(con, sql):
    return con.execute(sql).fetchone()[0]


def test_one_row_per_trial(con):
    assert count(con, "SELECT count(*) FROM fact_trial") == 3
    assert count(con, "SELECT count(DISTINCT nct_id) FROM fact_trial") == 3


def test_dates_are_typed(con):
    assert count(con, "SELECT count(*) FROM fact_trial WHERE start_date IS NULL") == 0


def test_dimensions_are_deduplicated(con):
    assert count(con, "SELECT count(*) FROM dim_sponsor") == 2
    assert count(con, "SELECT count(*) FROM dim_condition") == 3  # case and spaces normalised


def test_bridges_point_at_real_rows(con):
    assert count(con, "SELECT count(*) FROM bridge_trial_condition") == 4
    assert count(con, """SELECT count(*) FROM bridge_trial_condition b
                         LEFT JOIN dim_condition d USING (condition_key)
                         LEFT JOIN fact_trial f USING (nct_id)
                         WHERE d.condition_key IS NULL OR f.nct_id IS NULL""") == 0


def test_chunks_follow_sections(con):
    sections = con.execute("SELECT section FROM trial_chunk WHERE nct_id = 'NCT1' ORDER BY 1").fetchall()
    assert [s[0] for s in sections] == ["exclusion", "inclusion", "summary"]
    assert count(con, "SELECT count(*) FROM trial_chunk WHERE nct_id = 'NCT3'") == 1  # empty text skipped


def test_search_returns_each_trial_once(con):
    result = search(con, fake_embed(["query"])[0])
    assert sorted(result.nct_id) == ["NCT1", "NCT2", "NCT3"]
    assert list(search(con, fake_embed(["query"])[0], phases=["PHASE3"]).nct_id) == []
