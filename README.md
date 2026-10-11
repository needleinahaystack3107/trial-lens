# Trial Lens

Describe a patient in plain words and find recruiting clinical trials whose eligibility text
fits. A small project for learning **data engineering for AI** on real
life-sciences data.

> A learning project. Not medical advice.

## How it works

```
ClinicalTrials.gov API
  -> bronze   raw JSON, as received
  -> silver   one clean row per trial
  -> gold     star schema: fact_trial + sponsor / condition / intervention
  -> chunks   summary, inclusion, exclusion text, each with an embedding
  -> app      your query -> vector -> nearest chunks, filtered by phase
```

Everything runs in [DuckDB](https://duckdb.org), including the vector search. Embeddings are
computed locally with [fastembed](https://github.com/qdrant/fastembed). No API keys, no paid
services. About 300 lines of Python.

## Run it

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

The repository ships with the data in `data/gold`, so the app works straight away. To rebuild it
from the live API:

```bash
.venv/bin/python -m pipeline.run
```

Tests (no network needed):

```bash
.venv/bin/python -m pytest -q
```

## Host it for free

On [Streamlit Community Cloud](https://share.streamlit.io): New app -> pick this repository,
branch `main`, file `app.py`.

## Learn

| Day | Lesson |
|---|---|
| 1 | [Bronze, silver, gold](learn/day-01-bronze-silver-gold.md) |
| 2 | [Idempotent ingestion and pagination](learn/day-02-idempotent-ingestion.md) |
| 3 | [Star schema and bridge tables](learn/day-03-star-schema.md) |
| 4 | [Data quality checks as tests](learn/day-04-data-quality-tests.md) |
| 5 | [Chunking clinical text](learn/day-05-chunking.md) |

More are planned in [docs/plan.md](docs/plan.md). A GitHub Action refreshes the data every day
and records it in [learn/LOG.md](learn/LOG.md).

## How it was built

Brainstorm -> [design](docs/design.md) -> [plan](docs/plan.md) -> implement one small task at a
time. Working rules for coding sessions are in [CLAUDE.md](CLAUDE.md).
