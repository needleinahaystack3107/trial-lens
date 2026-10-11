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
        with st.expander(f"Best matching text ({row.section})"):
            st.write(row.text)
