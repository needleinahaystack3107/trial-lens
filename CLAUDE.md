# trial-lens

A student-sized project that teaches data engineering for AI on public clinical trial data:
ClinicalTrials.gov API -> bronze -> silver -> gold star schema -> embedded chunks -> search app.

## Commands

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # setup
.venv/bin/python -m pytest -q                                        # tests (no network)
.venv/bin/python -m pipeline.run                                     # rebuild data/gold
.venv/bin/streamlit run app.py                                       # app
```

## Rules

- **Layers.** `data/bronze` is raw and never edited by hand. `silver_trial` is one clean row per
  trial. Gold is the star schema plus `trial_chunk`. The app reads only `data/gold/*.parquet`.
- **Minimal code.** Target under 400 lines of Python. No new dependency, class or abstraction
  unless a lesson in `learn/` explains why it is needed. SQL in DuckDB before Python loops.
- **Python 3.9 compatible** (no `X | Y` type hints, no `match`).
- **Every pipeline change gets a test** in `tests/test_pipeline.py`, written as a data quality check.
- **Deterministic output.** Gold files are sorted and vectors rounded so unchanged data produces
  unchanged files, and the daily job makes no commit.

## Cost guardrails (hard rules)

- Never add a paid API, API key, or paid service. Embeddings run locally with `fastembed`.
- Never enable extra usage / pay-per-token on the Claude account.
- When working with Claude: no subagents, quiet commands, do not re-read files just written.
  Check usage before each task; stop at 80% of the 5-hour window or 85% of the weekly limit,
  commit, tick the task in `docs/plan.md`, and set a one-time reminder for after the reset.
- Model choice: Sonnet for code, Haiku for lessons and README edits, Opus only for design changes.

## Adding a daily lesson

1. Pick the next unticked lesson in `docs/plan.md`.
2. Write `learn/day-NN-topic.md`: the idea in plain words, where it lives in the code, one
   "try it" exercise. Keep it under 200 words.
3. If the lesson needs code, add the smallest change that demonstrates it, with a test.

## Commits

- Author and committer are Abhijit Haridas only (repo-local git config, GitHub noreply email).
- About one commit in ten may carry a `Co-Authored-By: Claude` trailer; the rest carry none.
- No "Generated with" lines.

## Refine me (open questions to revisit while coding)

- Chunks are cut at 1500 characters; long criteria lose their tail. Split into several chunks?
- Every run re-embeds everything. Embed only new or changed chunks (lesson 8).
- There is no retrieval evaluation yet (lesson 7): a small set of query -> expected trial pairs.
- Conditions are only lower-cased; map them to a vocabulary such as MeSH?
