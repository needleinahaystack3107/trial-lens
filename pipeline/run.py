"""Run every stage in order: bronze -> silver -> gold -> chunks -> parquet."""
from pathlib import Path

import duckdb

from pipeline import chunk_embed, ingest, model, transform

GOLD = ["fact_trial", "dim_sponsor", "dim_condition", "dim_intervention",
        "bridge_trial_condition", "bridge_trial_intervention", "trial_chunk"]


def main(data_dir="data"):
    bronze, gold = Path(data_dir) / "bronze", Path(data_dir) / "gold"
    gold.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    ingest.run(bronze)
    transform.run(con, bronze)
    model.run(con)
    chunk_embed.run(con)
    for table in GOLD:  # sorted output, so unchanged data gives unchanged files
        con.execute(f"COPY (SELECT * FROM {table} ORDER BY 1, 2) TO '{gold / table}.parquet'")
    trials, chunks = con.execute(
        "SELECT (SELECT count(*) FROM fact_trial), (SELECT count(*) FROM trial_chunk)").fetchone()
    print(f"{trials} trials, {chunks} chunks")


if __name__ == "__main__":
    main()
