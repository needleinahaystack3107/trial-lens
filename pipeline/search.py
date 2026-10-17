"""Retrieval: vector similarity and star-schema filters in one SQL query."""
from pathlib import Path

import duckdb


def load(gold_dir="data/gold"):
    con = duckdb.connect()
    for f in sorted(Path(gold_dir).glob("*.parquet")):
        con.execute(f"CREATE TABLE {f.stem} AS SELECT * FROM '{f}'")
    return con


def search(con, query_vector, phases=None, k=10):
    """Best summary or inclusion chunk per trial, optionally filtered by phase.

    Exclusion chunks never count as a match: a patient "with kidney disease" should not find a
    trial because it *excludes* kidney disease. Their best score is returned so the app can warn.
    """
    params = [query_vector]
    phase_filter = ""
    if phases:
        phase_filter = "AND f.phase IN (SELECT unnest(?))"
        params.append(phases)
    return con.execute(f"""
        WITH scored AS (
            SELECT nct_id, section, text,
                   array_cosine_similarity(embedding::FLOAT[384], ?::FLOAT[384]) AS score
            FROM trial_chunk),
        exclusion AS (
            SELECT nct_id, max(score) AS exclusion_score
            FROM scored WHERE section = 'exclusion' GROUP BY nct_id)
        SELECT f.nct_id, f.title, f.phase, s.name AS sponsor, b.section, b.text, b.score,
               x.exclusion_score
        FROM scored b
        JOIN fact_trial f USING (nct_id)
        JOIN dim_sponsor s USING (sponsor_key)
        LEFT JOIN exclusion x USING (nct_id)
        WHERE b.section <> 'exclusion' {phase_filter}
        QUALIFY row_number() OVER (PARTITION BY b.nct_id ORDER BY b.score DESC) = 1
        ORDER BY b.score DESC LIMIT {int(k)}
    """, params).df()
