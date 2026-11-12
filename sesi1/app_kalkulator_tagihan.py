
import streamlit as st

# Konfigurasi halaman
st.set_page_config(
    page_title="Kalkulator Tagihan",
    page_icon="📋",
    layout="centered"
)

# Judul aplikasi
st.title("📋 Kalkulator Estimasi Tagihan Internet")
st.write("Masukkan paket dan durasi berlangganan untuk melihat estimasi biaya.")

# Daftar harga layanan
HARGA = {
    "DSL": 260_000,
    "Fiber": 420_000,
    "Mobile Broadband": 310_000,
    "Satelit": 550_000
}

# Daftar diskon kontrak
DISKON = {
    "Bulanan": 0.00,
    "Tahunan": 0.10,
    "Dua Tahun": 0.18
}

# Input layanan
layanan = st.selectbox(
    "Jenis layanan",
    list(HARGA),
    key="pilihan_layanan"
)

# Input kontrak
kontrak = st.radio(
    "Jenis kontrak",
    list(DISKON),
    horizontal=True,
    key="pilihan_kontrak"
)

# Input durasi
bulan = st.number_input(
    "Durasi (bulan)",
    min_value=1,
    max_value=72,
    value=12,
    step=1,
    key="durasi"
)

# Slider diskon promosi
promo = st.slider(
    "Diskon promosi tambahan (%)",
    min_value=0,
    max_value=20,
    value=0,
    step=1,
    key="diskon_promo"
)

# Checkbox PPN
ppn = st.checkbox(
    "Tambahkan PPN 11%",
    value=True,
    key="pilihan_ppn"
)

# Tombol hitung
if st.button("Hitung", type="primary", key="tombol_hitung"):

    harga_awal = HARGA[layanan]

    # Diskon kontrak
    harga_kontrak = harga_awal * (1 - DISKON[kontrak])

    # Diskon promosi
    per_bulan = harga_kontrak * (1 - promo / 100)

    # Total tagihan
    subtotal = per_bulan * bulan

    # PPN 11%
    total = subtotal * 1.11 if ppn else subtotal

    # Hasil perhitungan
    st.divider()
    st.subheader("Hasil Perhitungan")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Harga Awal per Bulan",
            f"Rp{harga_awal:,.0f}".replace(",", ".")
        )

    with col2:
        st.metric(
            "Biaya per Bulan",
            f"Rp{per_bulan:,.0f}".replace(",", ".")
        )

    st.metric(
        "Total Estimasi Tagihan",
        f"Rp{total:,.0f}".replace(",", ".")
    )

    st.write(f"Jenis layanan: {layanan}")
    st.write(f"Jenis kontrak: {kontrak}")
    st.write(f"Diskon kontrak: {DISKON[kontrak]:.0%}")
    st.write(f"Diskon promosi: {promo}%")
    st.write(f"Durasi: {bulan} bulan")
    st.write(f"PPN: {'11%' if ppn else 'Tidak dikenakan'}")

    st.caption("Estimasi bersifat ilustratif untuk latihan.")
