# streamlit_app.py — Dashboard Customer Churn, Sesi 3 (Dynamic Layout with Streamlit)
# Entrypoint multipage: halaman Praktikum 3.3 dan Latihan Mandiri.
# Lokal: streamlit run streamlit_app.py
import streamlit as st

st.set_page_config(page_title="Dashboard Customer Churn", page_icon="📊", layout="wide")

halaman = st.navigation([
    st.Page("praktikum.py", title="Praktikum 3.3", icon="📊", default=True),
    st.Page("latihan.py", title="Latihan Mandiri", icon="✍️"),
])
halaman.run()
