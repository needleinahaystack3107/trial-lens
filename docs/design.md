# Design

**Goal.** Type a patient description, get recruiting clinical trials whose eligibility text fits,
and learn one data-engineering-for-AI idea per day along the way.

**Source.** ClinicalTrials.gov API v2 (public, no key). About 100 recruiting trials for each of:
type 2 diabetes, breast cancer, Alzheimer disease.

## Flow

```
API -> ingest.py -> data/bronze/*.json      raw, as received
    -> transform.py -> silver_trial         typed, one row per trial
    -> model.py -> gold star schema         fact + dimensions + bridges
    -> chunk_embed.py -> trial_chunk        text + 384-number vector
    -> run.py -> data/gold/*.parquet        what the app reads
app.py: query -> vector -> cosine similarity in DuckDB -> trials
```

## Data model (gold)

| Table | Grain | Columns |
|---|---|---|
| `fact_trial` | one trial | nct_id, title, phase, status, enrollment, start_date, sponsor_key |
| `dim_sponsor` | one sponsor | sponsor_key, name, sponsor_class |
| `dim_condition` | one condition | condition_key, name |
| `dim_intervention` | one intervention | intervention_key, name, intervention_type |
| `bridge_trial_condition` | trial x condition | nct_id, condition_key |
| `bridge_trial_intervention` | trial x intervention | nct_id, intervention_key |
| `trial_chunk` | one section of one trial | chunk_id, nct_id, section, text, embedding |

## Choices

- **DuckDB for everything**, including vector search. One engine, no server, no vector database.
- **`fastembed` with `bge-small-en-v1.5`**: local, free, small enough for free hosting.
- **Chunk by section** (summary, inclusion, exclusion) rather than by length: the unit a
  clinician reasons about.
- **Parquet committed to the repo** so the hosted app needs no build step.
- **Daily GitHub Action** rebuilds gold and logs the run; no change means no commit.

## Out of scope

LLM-generated answers, user accounts, more than a few hundred trials, medical advice.
