"""AI layer: cut each trial into meaningful chunks and embed them."""
import re

MODEL = "BAAI/bge-small-en-v1.5"  # 384 dimensions, runs on a laptop CPU
MAX_CHARS = 1500  # roughly what the model can read in one go


def chunk(nct_id, summary, criteria):
    """Split on meaning, not on length: summary, inclusion, exclusion."""
    parts = re.split(r"exclusion criteria:?", criteria or "", maxsplit=1, flags=re.I)
    sections = {
        "summary": summary or "",
        "inclusion": re.sub(r"inclusion criteria:?", "", parts[0], flags=re.I),
        "exclusion": parts[1] if len(parts) > 1 else "",
    }
    return [
        (f"{nct_id}:{name}", nct_id, name, text.strip()[:MAX_CHARS])
        for name, text in sections.items()
        if text.strip()
    ]


def embed_texts(texts):
    from fastembed import TextEmbedding

    # Rounding keeps the saved files identical when the data has not changed.
    return [v.round(4).tolist() for v in TextEmbedding(MODEL).embed(texts)]


def run(con, embed=embed_texts):
    rows = con.execute("SELECT nct_id, summary, criteria FROM silver_trial ORDER BY nct_id").fetchall()
    chunks = [c for row in rows for c in chunk(*row)]
    vectors = embed([c[3] for c in chunks])
    con.execute("""CREATE OR REPLACE TABLE trial_chunk (
        chunk_id VARCHAR, nct_id VARCHAR, section VARCHAR, text VARCHAR, embedding FLOAT[384])""")
    con.executemany("INSERT INTO trial_chunk VALUES (?, ?, ?, ?, ?)",
                    [c + (v,) for c, v in zip(chunks, vectors)])
