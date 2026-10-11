# Day 3: Star schema and bridge tables

**Idea.** Put the thing you count in a *fact* table (one row per trial) and the things you
filter or group by in *dimension* tables (sponsor, condition, intervention). A sponsor's name is
stored once and referenced by key.

A trial can study several conditions and a condition has many trials. That many-to-many link
does not fit in one column, so it gets its own *bridge* table with one row per pair.

**In the code.** `pipeline/model.py` is plain SQL: `fact_trial`, three `dim_` tables and two
`bridge_` tables. The table list is in `docs/design.md`.

**Why it matters for AI.** Vector search finds similar text; it cannot answer "only phase 3" or
"only industry sponsors". The star schema supplies those filters, and `pipeline/search.py`
combines both in one query.

**Try it.** Write a query for the five conditions with the most recruiting trials.
