# sesi1/latihan_profil.py — Latihan Mandiri Sesi 1 no. 3: aplikasi "Profil Peserta"
# Jalankan: streamlit run sesi1/latihan_profil.py
import streamlit as st

st.set_page_config(page_title="Profil Peserta", page_icon="🙋")
st.title("🙋 Profil Peserta")

nama = st.text_input("Nama")
divisi = st.selectbox("Divisi", ["Finance", "Operations", "Marketing", "IT", "HR"])
pengalaman = st.slider("Pengalaman (tahun)", 0, 30, 2)

if nama:
    st.info(f"{nama} dari divisi {divisi} dengan pengalaman {pengalaman} tahun.")
else:
    st.caption("Isi nama untuk melihat ringkasan profil.")
