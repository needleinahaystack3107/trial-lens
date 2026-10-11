# Day 1: Bronze, silver, gold

**Idea.** Keep data in three layers. *Bronze* is the raw copy, exactly as the source sent it.
*Silver* is cleaned: right types, no duplicates. *Gold* is shaped for the people (or models)
that use it. When something looks wrong in gold you can walk back to bronze and see whether the
source or your code is to blame, and you can rebuild everything without calling the API again.

**In the code.** `pipeline/ingest.py` writes bronze JSON. `pipeline/transform.py` builds
`silver_trial`. `pipeline/model.py` builds gold. `pipeline/run.py` runs them in order.

**Why it matters for AI.** A model's answer is only as traceable as its data. If a search result
looks odd, the layers let you answer "what did the source actually say?"

**Try it.** Open one file in `data/bronze/` and find a field that silver drops. Would a search
user ever want it?
