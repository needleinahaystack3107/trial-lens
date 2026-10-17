"""Run every stage in order: bronze -> silver -> gold -> chunks -> parquet."""
from pathlib import Path

import duckdb

from pipeline import chunk_embed, ingest, model, transform

GOLD = ["fact_trial", "dim_sponsor", "dim_condition", "dim_intervention",
        "bridge_trial_condition", "bridge_trial_intervention", "trial_chunk"]


def write_if_changed(con, table, path):
    """Rewrite a file only when its rows changed. A newer DuckDB can write the same rows as
    different bytes, and that should not count as a data change (or a daily commit)."""
    if path.exists():
        diff = con.execute(f"""SELECT count(*) FROM (
            (SELECT * FROM {table} EXCEPT ALL SELECT * FROM read_parquet('{path}'))
            UNION ALL
            (SELECT * FROM read_parquet('{path}') EXCEPT ALL SELECT * FROM {table}))""").fetchone()[0]
        if diff == 0:
            return
    con.execute(f"COPY (SELECT * FROM {table} ORDER BY ALL) TO '{path}' (FORMAT parquet)")


def main(data_dir="data"):
    bronze, gold = Path(data_dir) / "bronze", Path(data_dir) / "gold"
    gold.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    ingest.run(bronze)
    transform.run(con, bronze)
    model.run(con)
    chunk_embed.run(con)
    for table in GOLD:
        write_if_changed(con, table, gold / f"{table}.parquet")
    trials, chunks = con.execute(
        "SELECT (SELECT count(*) FROM fact_trial), (SELECT count(*) FROM trial_chunk)").fetchone()
    print(f"{trials} trials, {chunks} chunks")


if __name__ == "__main__":
    main()
