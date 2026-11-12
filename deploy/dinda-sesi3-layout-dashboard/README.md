# Dashboard Customer Churn — Sesi 3

Dashboard Streamlit multipage (Buku Praktikum Interactive Dashboard Development
with Streamlit & Dash, Sesi 3 — Dynamic Layout with Streamlit).

- `streamlit_app.py` — entrypoint, navigasi dua halaman (`st.navigation`)
- `praktikum.py` — halaman **Praktikum 3.3**: sidebar filter, 4 KPI, tab Ringkasan/Segmentasi/Data Detail
- `latihan.py` — halaman **Latihan Mandiri** no. 1–5: filter layanan internet, KPI keluhan ≥ 3,
  churn per kuartal, container border, tombol Reset filter
- `data/customer_churn.csv` — data latihan sintetis, 3.000 pelanggan
- `requirements.txt` — library yang dipasang Streamlit Cloud

Jalankan lokal: `streamlit run streamlit_app.py`
