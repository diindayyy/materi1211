# streamlit_app.py — Prediksi Churn, Sesi 4 (ML Model Inference & Dashboard Integration)
# Entrypoint multipage: halaman Praktikum 4.5 dan Latihan Mandiri.
# Lokal: streamlit run streamlit_app.py
import streamlit as st

st.set_page_config(page_title="Prediksi Churn", page_icon="🤖", layout="wide")

halaman = st.navigation([
    st.Page("praktikum.py", title="Praktikum 4.5", icon="🤖", default=True),
    st.Page("latihan.py", title="Latihan Mandiri", icon="✍️"),
])
halaman.run()
