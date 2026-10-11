# Day 4: Data quality checks as tests

**Idea.** Code tests ask "does the function work?". Data tests ask "is the table still true?".
The useful ones are simple statements about the data: one row per trial, no missing dates, every
key in a bridge points at a real row.

Run them on a tiny hand-made input where you know the right answer, including the awkward
cases: a trial that appears twice, a date with no day, a condition spelled with different case.

**In the code.** `tests/test_pipeline.py` builds three fake trials and checks each layer. It
needs no network and no model, so it runs in seconds.

**Why it matters for AI.** A broken join does not raise an error in a search app. It silently
returns fewer or stranger results. Tests are how you find out before a user does.

**Try it.** Remove the `QUALIFY` line in `pipeline/transform.py` and see which test fails.
