# Day 5: Chunking clinical text

**Idea.** An embedding model turns a piece of text into one vector. Embed a whole trial and the
vector is a blur of everything in it. Embed pieces that each say one thing and a query can match
the piece that matters. Choosing those pieces is *chunking*.

Cutting every N characters is the common default, but it slices sentences in half. Clinical
trials already have structure, so we cut on meaning: summary, inclusion criteria, exclusion
criteria.

**In the code.** `chunk()` in `pipeline/chunk_embed.py`. Each chunk keeps its `nct_id` and
`section`, so a result can say *why* it matched.

**A trap.** A patient "with kidney disease" can match a trial that *excludes* kidney disease,
because the words are similar. Keeping `section` on every chunk lets the app show that.

**Try it.** Search for a condition and count how many top results matched on `exclusion`.
