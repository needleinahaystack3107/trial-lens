# Plan

Workflow: brainstorm -> design (`design.md`) -> this plan -> implement one task at a time
(test, code, lesson, commit) -> verify.

## Build

- [x] 1. Design, plan and CLAUDE.md
- [x] 2. Bronze: paginated, idempotent ingestion — `pipeline/ingest.py`
- [x] 3. Silver: flatten, type, de-duplicate — `pipeline/transform.py`
- [x] 4. Gold: star schema with bridges — `pipeline/model.py`
- [x] 5. Data quality tests — `tests/test_pipeline.py`
- [x] 6. Chunk and embed — `pipeline/chunk_embed.py`
- [x] 7. Search and app — `pipeline/search.py`, `app.py`
- [x] 8. Runner and committed gold parquet — `pipeline/run.py`
- [x] 9. Daily refresh workflow — `.github/workflows/daily.yml`
- [ ] 10. Push to GitHub and confirm the workflow is green
- [ ] 11. Deploy on Streamlit Community Cloud

## Lessons

- [x] Day 1: bronze, silver, gold
- [x] Day 2: idempotent ingestion and pagination
- [x] Day 3: star schema and bridge tables
- [x] Day 4: data quality checks as tests
- [x] Day 5: chunking clinical text
- [ ] Day 6: embeddings and vector storage
- [ ] Day 7: retrieval and how to evaluate it
- [ ] Day 8: scheduling and incremental refresh
