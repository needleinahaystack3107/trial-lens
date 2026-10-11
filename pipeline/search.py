"""Retrieval: vector similarity and star-schema filters in one SQL query."""
from pathlib import Path

import duckdb


def load(gold_dir="data/gold"):
    con = duckdb.connect()
    for f in sorted(Path(gold_dir).glob("*.parquet")):
        con.execute(f"CREATE TABLE {f.stem} AS SELECT * FROM '{f}'")
    return con


def search(con, query_vector, phases=None, k=10):
    """Best-matching chunk per trial, optionally filtered by phase."""
    params = [query_vector]
    phase_filter = ""
    if phases:
        phase_filter = "WHERE f.phase IN (SELECT unnest(?))"
        params.append(phases)
    return con.execute(f"""
        SELECT f.nct_id, f.title, f.phase, s.name AS sponsor, c.section, c.text,
               array_cosine_similarity(c.embedding::FLOAT[384], ?::FLOAT[384]) AS score
        FROM trial_chunk c
        JOIN fact_trial f USING (nct_id)
        JOIN dim_sponsor s USING (sponsor_key)
        {phase_filter}
        QUALIFY row_number() OVER (PARTITION BY f.nct_id ORDER BY score DESC) = 1
        ORDER BY score DESC LIMIT {int(k)}
    """, params).df()
