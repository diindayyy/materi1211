# Prediksi Risiko Churn — Sesi 4

Dashboard Streamlit multipage (Buku Praktikum Interactive Dashboard Development
with Streamlit & Dash, Sesi 4 — ML Model Inference & Dashboard Integration).
Model final dimuat dari file; aplikasi hanya melakukan inference, tanpa training ulang.

- `streamlit_app.py` — entrypoint, navigasi dua halaman (`st.navigation`)
- `praktikum.py` — halaman **Praktikum 4.5**: prediksi satu pelanggan (form) dan batch (CSV)
- `latihan.py` — halaman **Latihan Mandiri** no. 1–4: slider threshold, uji validasi,
  crosstab region × risiko, pendapatan berisiko
- `models/` — `churn_model.joblib` + `model_metadata.json` (model final fasilitator, v1.0.0)
- `utils/model_utils.py` — fungsi load, validasi, persiapan input, dan prediksi
- `data/new_customers.csv` — 200 pelanggan baru; `data/data_salah.csv` — contoh input tidak valid
- `requirements.txt` — scikit-learn dikunci 1.9.1 sesuai metadata model

Jalankan lokal: `streamlit run streamlit_app.py`
