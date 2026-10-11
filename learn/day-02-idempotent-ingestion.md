# Day 2: Idempotent ingestion and pagination

**Idea.** An *idempotent* job gives the same result whether you run it once or five times.
Pipelines fail and get re-run, so a job that appends on every run will sooner or later
duplicate data. The simplest fix is to overwrite a known location instead of appending.

APIs also return results a page at a time. Each response carries a token for the next page; you
loop until there is no token or you have enough rows.

**In the code.** `fetch()` in `pipeline/ingest.py` follows `nextPageToken`. `run()` writes one
file per condition and overwrites it each time.

**Why it matters for AI.** Duplicate rows become duplicate vectors, and the same trial then
fills several of your top ten results.

**Try it.** Run `python -m pipeline.run` twice. Check with `git status` that `data/gold` did not
change the second time.
