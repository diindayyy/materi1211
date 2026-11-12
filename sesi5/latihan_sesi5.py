# sesi5/latihan_sesi5.py — app_dash_dasar.py + Latihan Mandiri Sesi 5
# Jalankan: python sesi5/latihan_sesi5.py  lalu buka http://127.0.0.1:8050
# 1. KPI card kelima: rata-rata jumlah keluhan
# 2. Grafik kedua (churn rate per region), dua grafik berdampingan dengan CSS grid
# 3. DataTable dengan sort_action="native" dan page_size=5
# 4. Gaya dipindah ke sesi5/assets/style.css, komponen memakai className
from pathlib import Path

import pandas as pd
from dash import Dash, dash_table, dcc, html

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "customer_churn.csv", parse_dates=["signup_date"])


def ringkas_per(kolom):
    r = (df.groupby(kolom)
           .agg(pelanggan=("customer_id", "count"), churn_rate=("churn", "mean"))
           .reset_index())
    r["churn_rate"] = (r["churn_rate"] * 100).round(1)
    return r


ringkas = ringkas_per("contract_type")
per_region = ringkas_per("region").sort_values("churn_rate", ascending=False)

# assets_folder ditunjuk eksplisit agar sesi5/assets/style.css selalu termuat
app = Dash(__name__, title="Dash Dasar — Latihan",
           assets_folder=str(Path(__file__).resolve().parent / "assets"))


def kartu(judul, nilai):
    return html.Div([html.P(judul), html.H2(nilai)], className="kartu")


def grafik_bar(data, x, judul, warna):
    return dcc.Graph(figure={
        "data": [{"type": "bar", "x": data[x], "y": data["churn_rate"], "marker": {"color": warna},
                  "text": data["churn_rate"].astype(str) + "%", "textposition": "outside"}],
        "layout": {"title": {"text": judul}, "yaxis": {"title": {"text": "Churn rate (%)"},
                                                       "range": [0, 65]},
                   "height": 350, "margin": {"t": 50, "l": 50, "r": 10, "b": 40}},
    })


app.layout = html.Div(className="halaman", children=[
    html.H1("Dashboard Churn — Versi Dash"),
    html.P("Contoh layout statis: header, KPI cards, grafik, dan tabel."),

    html.Div(className="baris-kpi", children=[
        kartu("Total pelanggan", f"{len(df):,}"),
        kartu("Churn rate", f"{df.churn.mean():.1%}"),
        kartu("Rata-rata tenure", f"{df.tenure_months.mean():.1f} bln"),
        kartu("Region", df.region.nunique()),
        kartu("Rata-rata keluhan", f"{df.num_complaints.mean():.2f}"),  # Latihan 1
    ]),

    # Latihan 2: dua grafik berdampingan (CSS grid di assets/style.css)
    html.Div(className="grid-2", children=[
        grafik_bar(ringkas, "contract_type", "Churn rate per jenis kontrak", "#C44E52"),
        grafik_bar(per_region, "region", "Churn rate per region", "#4C72B0"),
    ]),

    html.H3("Ringkasan per kontrak"),
    dash_table.DataTable(
        data=ringkas.to_dict("records"),
        columns=[{"name": c, "id": c} for c in ringkas.columns],
        sort_action="native", page_size=5,  # Latihan 3
        style_cell={"padding": "6px", "textAlign": "left"},
        style_header={"fontWeight": "bold", "background": "#E9EDF5"},
    ),
    html.H3("Ringkasan per region"),
    dash_table.DataTable(
        data=per_region.to_dict("records"),
        columns=[{"name": c, "id": c} for c in per_region.columns],
        sort_action="native", page_size=5,
        style_cell={"padding": "6px", "textAlign": "left"},
        style_header={"fontWeight": "bold", "background": "#E9EDF5"},
    ),

    html.Hr(),
    html.Small("Sumber: data latihan sintetis customer_churn.csv"),
])

if __name__ == "__main__":
    app.run(debug=True, port=8050)
