# sesi2/latihan_sesi2_grafik.py — Latihan Mandiri Sesi 2 no. 1–4 (Matplotlib)
# Jalankan: python sesi2/latihan_sesi2_grafik.py  -> grafik tersimpan di sesi2/output/latihan/
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "sesi2" / "output" / "latihan"
OUT.mkdir(parents=True, exist_ok=True)

BIRU, ORANYE, HIJAU, KUNING, UNGU = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#4a3aa7"
WARNA = [BIRU, HIJAU, KUNING, UNGU, "#e87ba4"]
TEKS, TEKS2 = "#0b0b0b", "#52514e"
STATUS = {"Bertahan": BIRU, "Churn": ORANYE}
plt.rcParams.update({
    "figure.dpi": 110, "savefig.dpi": 200, "font.size": 10,
    "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": "#e6e5e0", "axes.axisbelow": True,
})


def simpan(fig, nama):
    fig.tight_layout()
    fig.savefig(OUT / nama, bbox_inches="tight", facecolor="white")
    plt.close(fig)


df = pd.read_csv(ROOT / "data" / "customer_churn.csv", parse_dates=["signup_date"])
df["status"] = df["churn"].map({0: "Bertahan", 1: "Churn"})

# ---------- 1a. Pie komposisi internet_service ----------
s = df["internet_service"].value_counts()
fig, ax = plt.subplots(figsize=(5, 4))
ax.pie(s, labels=s.index, autopct="%1.1f%%", colors=WARNA[:3], startangle=90,
       counterclock=False, wedgeprops=dict(edgecolor="white", linewidth=2))
ax.set_title("Komposisi layanan internet")
simpan(fig, "L1a_pie_internet_service.png")

# ---------- 1b. Donut komposisi region ----------
r = df["region"].value_counts()
fig, ax = plt.subplots(figsize=(5, 4))
ax.pie(r, labels=r.index, autopct="%1.0f%%", pctdistance=0.8, colors=WARNA, startangle=90,
       counterclock=False, wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2))
ax.set_title("Komposisi region (donut)")
simpan(fig, "L1b_donut_region.png")

# ---------- 1c. Pembanding: bar horizontal terurut untuk region ----------
rs = r.sort_values()
fig, ax = plt.subplots(figsize=(6.5, 3.6))
bars = ax.barh(rs.index, rs.values, color=BIRU, height=0.55)
ax.bar_label(bars, labels=[f"{v:,} ({v/len(df):.0%})".replace(",", ".") for v in rs.values],
             padding=3, color=TEKS)
ax.set(xlabel="Jumlah pelanggan", xlim=(0, rs.max() * 1.25))
ax.grid(axis="y", visible=False)
ax.set_title("Jawa mendominasi; bar terurut lebih mudah dibandingkan")
simpan(fig, "L1c_barh_region.png")

# ---------- 2. Stacked bar 100% status per internet_service ----------
ct = pd.crosstab(df["internet_service"], df["status"], normalize="index").sort_values("Churn") * 100
fig, ax = plt.subplots(figsize=(7, 3.2))
ax.barh(ct.index, ct["Bertahan"], color=BIRU, label="Bertahan", height=0.55)
ax.barh(ct.index, ct["Churn"], left=ct["Bertahan"], color=ORANYE, label="Churn", height=0.55)
for i, v in enumerate(ct["Churn"]):
    ax.text(100 - v / 2, i, f"{v:.1f}%", ha="center", va="center", color="white", fontweight="bold")
ax.set(xlabel="Proporsi pelanggan (%)", xlim=(0, 100))
ax.grid(axis="y", visible=False)
ax.legend(ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.22), frameon=False)
ax.set_title("Layanan internet bukan pembeda churn (porsi churn ~35%)")
simpan(fig, "L2_stacked_internet_service.png")

# ---------- 3. Box plot support_calls per status ----------
fig, ax = plt.subplots(figsize=(6, 4))
bp = ax.boxplot([df.loc[df.status == s, "support_calls"] for s in ["Bertahan", "Churn"]],
                tick_labels=["Bertahan", "Churn"], patch_artist=True, widths=0.5,
                medianprops=dict(color=TEKS))
for patch, s in zip(bp["boxes"], ["Bertahan", "Churn"]):
    patch.set_facecolor(STATUS[s])
    patch.set_alpha(0.55)
ax.set_ylabel("Panggilan ke CS")
ax.set_title("Median sama (2), tetapi sebaran panggilan CS pelanggan churn lebih lebar")
simpan(fig, "L3_box_support_calls.png")

# ---------- 4. Line chart churn rate per kuartal pendaftaran ----------
q = df.groupby(df.signup_date.dt.to_period("Q"))["churn"].mean() * 100
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.plot(q.index.astype(str), q.values, color=ORANYE, marker="o", linewidth=2)
ax.axhline(df.churn.mean() * 100, color=TEKS2, linestyle="--", linewidth=1)
ax.text(len(q) - 1, df.churn.mean() * 100 + 1.5, "rata-rata", ha="right", color=TEKS2, fontsize=9)
ax.set(xlabel="Kuartal pendaftaran", ylabel="Churn rate (%)", ylim=(0, None))
ax.tick_params(axis="x", rotation=45)
ax.set_title("Churn rate per kuartal pendaftaran")
simpan(fig, "L4_line_churn_kuartal.png")

# ---------- Ringkasan angka di terminal ----------
print("Porsi churn per layanan internet (%):")
print(ct["Churn"].round(1))
print("\nMedian support_calls:", df.groupby("status")["support_calls"].median().to_dict())
print("\nChurn rate per kuartal (%):")
print(q.round(1))
print("\nJawaban no. 1: untuk 5 region, bar horizontal terurut lebih mudah dibaca daripada donut,")
print("karena perbedaan panjang batang langsung terlihat; sudut irisan yang mirip sulit dibandingkan.")
print("\n6 grafik tersimpan di", OUT)
