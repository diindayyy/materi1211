# eda.py — Tab EDA Prediksi: EDA ala Sesi 2 (app_eda.py), diterapkan pada OUTPUT model Sesi 4
# Yang dieksplorasi: churn_probability, predicted_churn, risk_category hasil batch inference.
# Dipanggil dari praktikum.py sebagai tab pertama: tampilkan_eda()
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
from utils.model_utils import load_metadata, load_model, predict

RISK_ORDER = ["Rendah", "Sedang", "Tinggi"]
RISK_COLOR = {"Rendah": "#1baf7a", "Sedang": "#eda100", "Tinggi": "#e34948"}
PRED_COLOR = {"Bertahan": "#2a78d6", "Churn": "#eb6834"}
KATEGORI = ["#2a78d6", "#1baf7a", "#eda100", "#4a3aa7", "#e87ba4"]
KONTRAK = ["Bulanan", "Tahunan", "Dua Tahun"]
SUMBER = {
    "Pelanggan baru — new_customers.csv (200)": "new_customers.csv",
    "Data historis — customer_churn.csv (3.000)": "customer_churn.csv",
}


@st.cache_resource
def get_model():
    return load_model()


@st.cache_data
def get_meta():
    return load_metadata()


@st.cache_data
def hasil_prediksi(nama_file: str) -> pd.DataFrame:
    """Batch inference sekali per sumber data, lalu disimpan di cache."""
    data = pd.read_csv(ROOT / "data" / nama_file)
    if "signup_date" in data.columns:
        data["signup_date"] = pd.to_datetime(data["signup_date"])
    if data["total_charges"].isna().any():  # aturan penyiapan input yang sama dengan Sesi 8
        data["total_charges"] = data["total_charges"].fillna(
            data["monthly_charges"] * data["tenure_months"])
    out = predict(get_model(), data, get_meta())
    out["prediksi"] = out["predicted_churn"].map({0: "Bertahan", 1: "Churn"})
    out["kelompok_tenure"] = pd.cut(out["tenure_months"], [0, 12, 24, 48, 72],
                                    labels=["0-12", "13-24", "25-48", "49-72"]).astype(str)
    return out


def gaya(fig, tinggi=360):
    fig.update_layout(template="plotly_white", height=tinggi, margin=dict(l=10, r=10, t=50, b=10),
                      title_font_size=15, legend_title_text="")
    return fig


def rupiah(x):
    return f"Rp{x:,.0f}".replace(",", ".")


def tampilkan_eda():
    meta = get_meta()
    THR = meta["decision_threshold"]

    st.subheader("📊 EDA Hasil Prediksi Churn")
    pilih = st.radio("Sumber data yang diprediksi", list(SUMBER), horizontal=True, key="eda_sumber")
    df = hasil_prediksi(SUMBER[pilih])
    historis = "churn" in df.columns
    st.caption(f"Eksplorasi output model final ({meta['model_name']} v{meta['model_version']}) · "
               f"{len(df):,} pelanggan · threshold {THR} · risiko Rendah < 0,30 ≤ Sedang < 0,60 ≤ Tinggi")

    # ---------- KPI CARDS ----------
    tinggi = df.risk_category == "Tinggi"
    k = st.columns(6 if historis else 5)
    k[0].metric("Pelanggan diprediksi", f"{len(df):,}")
    k[1].metric("Prediksi churn", f"{df.predicted_churn.sum():,}",
                f"{df.predicted_churn.mean():.1%} dari total", delta_color="off")
    k[2].metric("Rata-rata probabilitas", f"{df.churn_probability.mean():.1%}")
    k[3].metric("Risiko tinggi", f"{tinggi.sum():,}", f"{tinggi.mean():.1%} dari total", delta_color="off")
    k[4].metric("Pendapatan berisiko", rupiah(df.loc[tinggi, "monthly_charges"].sum()),
                help="Σ tagihan bulanan pelanggan berisiko Tinggi")
    if historis:
        k[5].metric("Churn aktual", f"{df.churn.mean():.1%}", help="Label asli di data historis")

    nama_tab = ["🥧 Komposisi", "📊 Perbandingan", "📈 Distribusi", "⏱️ Pola", "🔗 Hubungan", "📋 Data"]
    if historis:
        nama_tab.append("🎯 Aktual vs Prediksi")
    tab = st.tabs(nama_tab)

    # ---------- 1. KOMPOSISI: pie, donut, treemap ----------
    with tab[0]:
        c1, c2 = st.columns(2)
        pie = px.pie(df, names="prediksi", color="prediksi", color_discrete_map=PRED_COLOR,
                     title=f"{df.predicted_churn.mean():.0%} pelanggan diprediksi churn")
        pie.update_traces(textinfo="percent+label", textfont_size=14)
        c1.plotly_chart(gaya(pie), width="stretch")

        donut = px.pie(df, names="risk_category", hole=0.55, color="risk_category",
                       color_discrete_map=RISK_COLOR, category_orders={"risk_category": RISK_ORDER},
                       title=f"{tinggi.mean():.0%} pelanggan berisiko tinggi")
        donut.update_traces(textinfo="percent+label", sort=False)
        donut.add_annotation(text=f"<b>{len(df):,}</b><br>pelanggan", showarrow=False, font_size=16)
        c2.plotly_chart(gaya(donut), width="stretch")

        tm = df.groupby(["region", "segment"], as_index=False).agg(
            pelanggan=("customer_id", "count"), rata2_prob=("churn_probability", "mean"))
        tree = px.treemap(tm, path=[px.Constant("Semua"), "region", "segment"], values="pelanggan",
                          color="rata2_prob", color_continuous_scale="Reds",
                          title="Treemap: luas = jumlah pelanggan, warna = rata-rata probabilitas churn")
        st.plotly_chart(gaya(tree, 420), width="stretch")

    # ---------- 2. PERBANDINGAN: bar terurut + tabel, grouped bar, stacked 100% ----------
    with tab[1]:
        kolom = st.selectbox("Bandingkan hasil prediksi berdasarkan",
                             ["contract_type", "region", "segment", "payment_method", "internet_service"])
        rk = (df.groupby(kolom, as_index=False)
                .agg(pelanggan=("customer_id", "count"), rata2_prob=("churn_probability", "mean"),
                     prediksi_churn=("predicted_churn", "sum"),
                     risiko_tinggi=("risk_category", lambda s: (s == "Tinggi").sum()))
                .sort_values("rata2_prob"))
        bar = px.bar(rk, x="rata2_prob", y=kolom, orientation="h", text_auto=".1%",
                     color_discrete_sequence=["#eb6834"],
                     title=f"Rata-rata probabilitas churn per {kolom}")
        bar.add_vline(x=df.churn_probability.mean(), line_dash="dot", annotation_text="rata-rata")
        bar.update_xaxes(tickformat=".0%")
        c1, c2 = st.columns([3, 2])
        c1.plotly_chart(gaya(bar), width="stretch")
        tabel = rk.sort_values("rata2_prob", ascending=False)
        c2.dataframe(tabel.style.format({"rata2_prob": "{:.1%}"})
                          .background_gradient(subset=["rata2_prob"], cmap="Reds"),
                     width="stretch", hide_index=True)
        c2.download_button("⬇️ Unduh ringkasan (CSV)", tabel.to_csv(index=False).encode("utf-8"),
                           file_name=f"ringkasan_prediksi_per_{kolom}.csv", mime="text/csv")

        c3, c4 = st.columns(2)
        gb = df.groupby(["contract_type", "segment"], as_index=False)["churn_probability"].mean()
        grouped = px.bar(gb, x="contract_type", y="churn_probability", color="segment", barmode="group",
                         color_discrete_sequence=KATEGORI, category_orders={"contract_type": KONTRAK},
                         title="Grouped bar: rata-rata probabilitas, kontrak × segmen",
                         labels={"churn_probability": "Rata-rata probabilitas", "contract_type": ""})
        grouped.update_yaxes(tickformat=".0%")
        c3.plotly_chart(gaya(grouped), width="stretch")

        stacked = px.histogram(df, y="payment_method", color="risk_category", barnorm="percent",
                               color_discrete_map=RISK_COLOR,
                               category_orders={"risk_category": RISK_ORDER},
                               title="Stacked bar 100%: kategori risiko per pembayaran")
        stacked.update_layout(xaxis_title="Proporsi (%)", yaxis_title="")
        c4.plotly_chart(gaya(stacked), width="stretch")

    # ---------- 3. DISTRIBUSI: histogram probabilitas, histogram fitur, violin ----------
    with tab[2]:
        hp = px.histogram(df, x="churn_probability", color="risk_category", nbins=30,
                          color_discrete_map=RISK_COLOR, category_orders={"risk_category": RISK_ORDER},
                          marginal="box", title="Distribusi probabilitas churn (output model)",
                          labels={"churn_probability": "Probabilitas churn"})
        hp.add_vline(x=THR, line_dash="dash", annotation_text=f"threshold {THR}")
        st.plotly_chart(gaya(hp, 400), width="stretch")

        num = st.selectbox("Variabel numerik", ["tenure_months", "monthly_charges",
                                                "num_complaints", "support_calls"])
        c1, c2 = st.columns(2)
        hist = px.histogram(df, x=num, color="risk_category", barmode="overlay", opacity=0.7, nbins=30,
                            color_discrete_map=RISK_COLOR, category_orders={"risk_category": RISK_ORDER},
                            title=f"Histogram {num} per kategori risiko")
        c1.plotly_chart(gaya(hist, 400), width="stretch")
        vio = px.violin(df, x="contract_type", y="churn_probability", color="contract_type", box=True,
                        color_discrete_sequence=KATEGORI, category_orders={"contract_type": KONTRAK},
                        title="Violin probabilitas churn per kontrak",
                        labels={"churn_probability": "Probabilitas churn", "contract_type": ""})
        vio.update_yaxes(tickformat=".0%")
        c2.plotly_chart(gaya(vio, 400), width="stretch")

    # ---------- 4. POLA: tenure & keluhan (pengganti tren waktu; data baru tidak punya tanggal) ----------
    with tab[3]:
        c1, c2 = st.columns(2)
        kt = df.groupby("kelompok_tenure", as_index=False)["churn_probability"].mean()
        lt = px.line(kt, x="kelompok_tenure", y="churn_probability", markers=True,
                     text=kt["churn_probability"].map("{:.1%}".format),
                     color_discrete_sequence=["#eb6834"],
                     title="Probabilitas churn turun seiring bertambahnya tenure",
                     labels={"kelompok_tenure": "Kelompok tenure (bulan)",
                             "churn_probability": "Rata-rata probabilitas"})
        lt.update_traces(textposition="top center", marker_size=10)
        lt.update_yaxes(tickformat=".0%", range=[0, 0.85])
        c1.plotly_chart(gaya(lt), width="stretch")

        kel = df.groupby("num_complaints", as_index=False).agg(
            pelanggan=("customer_id", "count"), rata2_prob=("churn_probability", "mean"))
        lk = px.line(kel, x="num_complaints", y="rata2_prob", markers=True, hover_data=["pelanggan"],
                     color_discrete_sequence=["#e34948"],
                     title="Probabilitas churn per jumlah keluhan",
                     labels={"num_complaints": "Jumlah keluhan", "rata2_prob": "Rata-rata probabilitas"})
        lk.update_yaxes(tickformat=".0%", range=[0, 1])
        lk.update_xaxes(dtick=1)
        c2.plotly_chart(gaya(lk), width="stretch")

        if historis:
            q = (df.assign(kuartal=df.signup_date.dt.to_period("Q").astype(str))
                   .groupby("kuartal").agg(aktual=("churn", "mean"), prediksi=("churn_probability", "mean"))
                   .reset_index().melt("kuartal", var_name="seri", value_name="rate"))
            lq = px.line(q, x="kuartal", y="rate", color="seri", markers=True,
                         color_discrete_map={"aktual": "#2a78d6", "prediksi": "#eb6834"},
                         title="Tren churn aktual vs rata-rata prediksi per kuartal pendaftaran",
                         labels={"kuartal": "Kuartal pendaftaran", "rate": "Rate"})
            lq.update_yaxes(tickformat=".0%", range=[0, 0.6])
            st.plotly_chart(gaya(lq), width="stretch")
        else:
            st.caption("Data pelanggan baru tidak punya tanggal pendaftaran, jadi pola dilihat terhadap "
                       "tenure dan keluhan. Pilih data historis di atas untuk melihat tren per kuartal.")

    # ---------- 5. HUBUNGAN: scatter, heatmap korelasi, heatmap pivot ----------
    with tab[4]:
        c1, c2 = st.columns(2)
        sc = px.scatter(df, x="tenure_months", y="monthly_charges", color="risk_category", opacity=0.6,
                        color_discrete_map=RISK_COLOR, category_orders={"risk_category": RISK_ORDER},
                        hover_name="customer_id",
                        hover_data={"churn_probability": ":.1%", "contract_type": True,
                                    "num_complaints": True},
                        title="Tenure vs tagihan, warna = kategori risiko",
                        labels={"tenure_months": "Tenure (bulan)", "monthly_charges": "Tagihan (Rp)"})
        c1.plotly_chart(gaya(sc, 420), width="stretch")

        kol = ["tenure_months", "monthly_charges", "num_complaints", "support_calls", "churn_probability"]
        corr = df[kol + (["churn"] if historis else [])].corr()
        hm = px.imshow(corr.round(2), text_auto=True, color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                       title="Korelasi fitur dengan probabilitas churn")
        c2.plotly_chart(gaya(hm, 420), width="stretch")

        pv = pd.pivot_table(df, values="churn_probability", index="region", columns="segment",
                            aggfunc="mean")
        hm2 = px.imshow(pv * 100, text_auto=".1f", color_continuous_scale="Reds",
                        labels={"color": "Prob. (%)"},
                        title="Heatmap rata-rata probabilitas churn region × segmen (%)")
        st.plotly_chart(gaya(hm2, 360), width="stretch")

    # ---------- 6. DATA: profil + statistik + tabel ----------
    with tab[5]:
        profil = pd.DataFrame({"tipe": df.dtypes.astype(str), "missing": df.isna().sum(),
                               "unik": df.nunique()}).reset_index(names="kolom")
        c1, c2 = st.columns([2, 3])
        c1.markdown("**Profil kolom (termasuk kolom output model)**")
        c1.dataframe(profil, width="stretch", hide_index=True)
        c2.markdown("**Statistik deskriptif**")
        c2.dataframe(df.describe(include="number").T.round(3), width="stretch")
        st.markdown("**10 pelanggan dengan probabilitas churn tertinggi**")
        st.dataframe(df.sort_values("churn_probability", ascending=False).head(10), width="stretch",
                     hide_index=True,
                     column_config={"churn_probability": st.column_config.ProgressColumn(
                         "Probabilitas churn", min_value=0.0, max_value=1.0, format="%.2f")})

    # ---------- 7. AKTUAL vs PREDIKSI (hanya data historis) ----------
    if historis:
        with tab[6]:
            st.caption("Sebagian data historis juga dipakai saat model dilatih, jadi angka di sini "
                       "cenderung lebih bagus daripada kinerja pada pelanggan baru. Acuan yang adil: "
                       f"metrik holdout di metadata (ROC-AUC {meta['holdout_metrics']['roc_auc']}).")
            c1, c2 = st.columns(2)
            ar = (df.groupby("risk_category", as_index=False)["churn"].mean()
                    .set_index("risk_category").reindex(RISK_ORDER).reset_index())
            ba = px.bar(ar, x="risk_category", y="churn", color="risk_category", text_auto=".1%",
                        color_discrete_map=RISK_COLOR,
                        title="Churn aktual per kategori risiko: kategori konsisten dengan kenyataan",
                        labels={"risk_category": "Kategori risiko", "churn": "Churn rate aktual"})
            ba.update_yaxes(tickformat=".0%", range=[0, 1])
            c1.plotly_chart(gaya(ba).update_layout(showlegend=False), width="stretch")

            cm = pd.crosstab(df["churn"].map({0: "Bertahan", 1: "Churn"}), df["prediksi"])
            cm = cm.reindex(index=["Bertahan", "Churn"], columns=["Bertahan", "Churn"], fill_value=0)
            hc = px.imshow(cm, text_auto=True, color_continuous_scale="Blues",
                           labels={"x": "Prediksi", "y": "Aktual", "color": "Pelanggan"},
                           title=f"Matriks aktual vs prediksi (threshold {THR})")
            c2.plotly_chart(gaya(hc), width="stretch")
            aktif_tinggi = ((df.churn == 0) & tinggi).sum()
            st.info(f"**{aktif_tinggi} pelanggan yang masih aktif** (belum churn) masuk kategori risiko "
                    "tinggi — kandidat pertama daftar kerja tim retensi.")
