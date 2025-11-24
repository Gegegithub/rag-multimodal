import streamlit as st
from rag_core import answer

# Configuration de la page
st.set_page_config(page_title="TP RAG Multimodal", layout="wide")

st.title("RAG Multimodal (OpenAI + pgvector)")
st.write("Pose une question sur le corpus indexe (textes + images).")

query = st.text_input("Question :")

if st.button("Rechercher & Repondre") and query:
    with st.spinner('Recherche et generation en cours...'):
        resp, rows = answer(query, k=5)
        
        st.subheader("Reponse")
        st.write(resp)
        
        st.subheader("Contexte recupere (top-5)")
        for src, chunk, modality, score in rows:
            with st.expander(f"[{modality}] Score: {score:.3f} | Source: {src}"):
                st.write(chunk)