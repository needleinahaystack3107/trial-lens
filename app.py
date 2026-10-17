"""Trial Lens: describe a patient, find recruiting trials that fit."""
import streamlit as st
from fastembed import TextEmbedding

from pipeline.chunk_embed import MODEL
from pipeline.search import load, search

st.set_page_config(page_title="Trial Lens")
con = st.cache_resource(load)()
embedder = st.cache_resource(TextEmbedding)(MODEL)

st.title("Trial Lens")
st.caption("Semantic search over recruiting clinical trials. A learning project, not medical advice.")

query = st.text_input("Describe the patient", "adult with type 2 diabetes and kidney disease")
all_phases = [r[0] for r in con.execute("SELECT DISTINCT phase FROM fact_trial ORDER BY 1").fetchall()]
phases = st.multiselect("Phase", all_phases)

if query:
    vector = next(iter(embedder.query_embed(query))).tolist()
    for row in search(con, vector, phases).itertuples():
        st.markdown(f"**[{row.title}](https://clinicaltrials.gov/study/{row.nct_id})**")
        st.caption(f"{row.nct_id} · {row.phase} · {row.sponsor} · match {row.score:.2f}")
        if row.exclusion_score is not None and row.exclusion_score >= row.score:
            st.warning(f"The exclusion criteria match your description at least as well "
                       f"({row.exclusion_score:.2f}). Check them before assuming the patient fits.")
        with st.expander(f"Best matching text ({row.section})"):
            st.write(row.text)
