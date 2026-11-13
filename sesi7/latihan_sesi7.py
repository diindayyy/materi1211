# sesi7/latihan_sesi7.py — app_dash_callback.py + Latihan Mandiri Sesi 7
# Jalankan: python sesi7/latihan_sesi7.py  lalu buka http://127.0.0.1:8057
# 1. dcc.Checklist internet_service, dihubungkan ke filter_df()
# 2. Output kelima pada callback utama: histogram tenure yang ikut terfilter
# 3. Klik titik scatter -> detail pelanggan (ID, region, kontrak, keluhan) di html.Div
# 4. dcc.Store menyimpan hasil filter (to_dict("records")) sekali; callback tabel membaca dari store
# 5. Tantangan: selectedData (box/lasso select) pada scatter memfilter tabel
from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, State, callback, ctx, dash_table, dcc, html, no_update
from dash.exceptions import PreventUpdate

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "customer_churn.csv", parse_dates=["signup_date"])
df["status"] = df["churn"].map({0: "Bertahan", 1: "Churn"})
WARNA = {"Bertahan": "#4C72B0", "Churn": "#C44E52"}
KARTU = {"flex": 1, "padding": "14px", "borderRadius": "10px", "background": "#F4F6FA",
         "textAlign": "center"}
TABEL_COLS = ["customer_id", "region", "segment", "contract_type", "internet_service",
              "tenure_months", "monthly_charges", "num_complaints", "status"]
LAYANAN = sorted(df.internet_service.unique())

app = Dash(__name__, title="Dash Callback — Latihan")
server = app.server  # untuk deployment WSGI (PythonAnywhere / gunicorn)
app.layout = html.Div(style={"maxWidth": "1200px", "margin": "auto", "fontFamily": "Arial",
                             "padding": "0 16px"}, children=[
    html.H1("Latihan Mandiri Sesi 7 — Dash Callback System"),
    html.Details(open=True, style={"background": "#F4F6FA", "borderRadius": "10px",
                                   "padding": "10px 14px", "marginBottom": "16px"}, children=[
        html.Summary("📝 Daftar soal dan letak jawabannya", style={"fontWeight": "bold",
                                                                 "cursor": "pointer"}),
        html.Ol(style={"margin": "8px 0 0 0"}, children=[
            html.Li("✅ Checklist Layanan internet (dcc.Checklist) di panel filter, terhubung ke "
                    "filter_df() — KPI, chart, dan tabel ikut berubah."),
            html.Li("✅ Output kelima di callback utama: histogram Distribusi tenure (terfilter), "
                    "chart ketiga."),
            html.Li("✅ Klik satu titik di scatter → detail pelanggan (ID, region, kontrak, keluhan) "
                    "muncul di kotak abu-abu di bawah chart."),
            html.Li("✅ dcc.Store id=store-data menyimpan hasil filter sekali (to_dict('records')); "
                    "callback tabel membaca dari store ini."),
            html.Li("✅ Tantangan: Box/Lasso Select di scatter (mode seleksi sudah aktif, tinggal "
                    "drag) → tabel hanya berisi titik terpilih."),
        ]),
    ]),

    # ---- Panel filter ----
    html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                    "gap": "16px"}, children=[
        html.Div([html.Label("Region"),
                  dcc.Dropdown(id="dd-region", options=sorted(df.region.unique()), multi=True,
                               placeholder="Semua region")]),
        html.Div([html.Label("Segmen (opsi bergantung region)"),
                  dcc.Dropdown(id="dd-segment", multi=True, placeholder="Semua segmen")]),
        html.Div([html.Label("Jenis kontrak"),
                  dcc.RadioItems(id="rd-kontrak", inline=True, value="Semua",
                                 options=["Semua", "Bulanan", "Tahunan", "Dua Tahun"])]),
        html.Div([html.Label("Layanan internet"),  # Latihan 1
                  dcc.Checklist(id="ck-internet", options=LAYANAN, value=LAYANAN, inline=True)]),
    ]),
    html.Div(style={"marginTop": "12px"}, children=[
        html.Label("Tenure (bulan)"),
        dcc.RangeSlider(id="rs-tenure", min=1, max=72, step=1, value=[1, 72],
                        marks={i: str(i) for i in (1, 12, 24, 36, 48, 60, 72)}),
    ]),
    html.Div(style={"display": "flex", "flexWrap": "wrap", "gap": "8px", "alignItems": "center"},
             children=[
        html.Label("Minimal jumlah keluhan:"),
        dcc.Input(id="in-keluhan", type="number", min=0, max=10, value=0, style={"width": "70px"}),
        html.Button("Terapkan", id="btn-terapkan", n_clicks=0),
        html.Button("Reset filter", id="btn-reset", n_clicks=0),
        html.Span(id="info-keluhan", style={"color": "#666"}),
    ]),
    dcc.Store(id="store-keluhan", data=0),
    dcc.Store(id="store-data"),  # Latihan 4: hasil filter disimpan sekali

    # ---- KPI ----
    html.Div(id="kpi", style={"display": "flex", "flexWrap": "wrap", "gap": "12px",
                              "margin": "16px 0"}),

    # ---- Charts ----
    html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(380px, 1fr))",
                    "gap": "12px"}, children=[
        dcc.Graph(id="g-bar"), dcc.Graph(id="g-scatter"), dcc.Graph(id="g-hist")]),
    html.Div(id="detail-pelanggan",  # Latihan 3
             style={"background": "#F4F6FA", "borderRadius": "10px", "padding": "10px 14px"},
             children="Klik satu titik pada scatter untuk melihat detail pelanggan."),
    html.P("Tip: klik batang region untuk memfilter tabel; atau pakai Box/Lasso Select di scatter.",
           style={"color": "#666"}),
    html.H3(id="judul-tabel"),
    dash_table.DataTable(id="tbl", page_size=10, sort_action="native",
                         columns=[{"name": c, "id": c} for c in TABEL_COLS],
                         style_table={"overflowX": "auto"},
                         style_cell={"padding": "6px", "textAlign": "left"},
                         style_header={"fontWeight": "bold", "background": "#E9EDF5"},
                         style_data_conditional=[{"if": {"filter_query": "{status} = 'Churn'"},
                                                  "backgroundColor": "#FBE9EA"}]),
])


def filter_df(region, segment, kontrak, tenure, min_keluhan, layanan):
    d = df
    if region:
        d = d[d.region.isin(region)]
    if segment:
        d = d[d.segment.isin(segment)]
    if kontrak and kontrak != "Semua":
        d = d[d.contract_type == kontrak]
    d = d[d.internet_service.isin(layanan or [])]  # Latihan 1
    d = d[d.tenure_months.between(tenure[0], tenure[1])]
    return d[d.num_complaints >= (min_keluhan or 0)]


# 1) Chained callback: opsi segmen bergantung pada region terpilih
@callback(Output("dd-segment", "options"), Input("dd-region", "value"))
def update_segment_options(region):
    d = df[df.region.isin(region)] if region else df
    return sorted(d.segment.unique())


# 2) State + tombol Terapkan / Reset
@callback(Output("store-keluhan", "data"), Output("in-keluhan", "value"),
          Output("dd-region", "value"), Output("dd-segment", "value"),
          Output("rd-kontrak", "value"), Output("rs-tenure", "value"),
          Output("ck-internet", "value"),
          Input("btn-terapkan", "n_clicks"), Input("btn-reset", "n_clicks"),
          State("in-keluhan", "value"), prevent_initial_call=True)
def terapkan_atau_reset(n_apply, n_reset, nilai):
    if ctx.triggered_id == "btn-reset":
        return 0, 0, None, None, "Semua", [1, 72], LAYANAN
    if nilai is None:
        raise PreventUpdate
    return nilai, no_update, no_update, no_update, no_update, no_update, no_update


# 3) Callback utama: filter -> KPI, 3 chart (Latihan 2: histogram), info, store data (Latihan 4)
@callback(Output("kpi", "children"), Output("g-bar", "figure"), Output("g-scatter", "figure"),
          Output("g-hist", "figure"), Output("info-keluhan", "children"),
          Output("store-data", "data"),
          Input("dd-region", "value"), Input("dd-segment", "value"), Input("rd-kontrak", "value"),
          Input("rs-tenure", "value"), Input("store-keluhan", "data"), Input("ck-internet", "value"))
def update_dashboard(region, segment, kontrak, tenure, min_keluhan, layanan):
    d = filter_df(region, segment, kontrak, tenure, min_keluhan, layanan)
    info = f"Filter keluhan aktif: ≥ {min_keluhan}"
    if d.empty:
        kosong = px.scatter(title="Tidak ada data untuk filter ini")
        return [html.Div("Data kosong", style=KARTU)], kosong, kosong, kosong, info, []

    def kartu(j, v):
        return html.Div([html.Small(j), html.H2(v, style={"margin": "4px 0"})], style=KARTU)

    kpi = [kartu("Pelanggan", f"{len(d):,}"), kartu("Churn rate", f"{d.churn.mean():.1%}"),
           kartu("Rata-rata tagihan", f"Rp{d.monthly_charges.mean():,.0f}".replace(",", ".")),
           kartu("Rata-rata keluhan", f"{d.num_complaints.mean():.2f}")]

    reg = d.groupby("region", as_index=False)["churn"].mean().sort_values("churn", ascending=False)
    bar = px.bar(reg, x="region", y="churn", template="plotly_white", title="Churn rate per region",
                 labels={"churn": "Churn rate", "region": ""}, color_discrete_sequence=["#C44E52"])
    bar.update_yaxes(tickformat=".0%")
    sc = px.scatter(d, x="tenure_months", y="monthly_charges", color="status", opacity=0.6,
                    color_discrete_map=WARNA, template="plotly_white", hover_name="customer_id",
                    custom_data=["customer_id"],  # untuk Latihan 3 & 5
                    title="Tenure vs tagihan", labels={"tenure_months": "Tenure (bulan)",
                                                       "monthly_charges": "Tagihan (Rp)"})
    sc.update_layout(dragmode="select")
    hist = px.histogram(d, x="tenure_months", color="status", nbins=24, barmode="overlay",
                        opacity=0.7, color_discrete_map=WARNA, template="plotly_white",
                        title="Distribusi tenure (terfilter)",
                        labels={"tenure_months": "Tenure (bulan)", "status": "Status"})
    return kpi, bar, sc, hist, info, d[TABEL_COLS].to_dict("records")


# 4) Tabel membaca dari store; klik batang (region) atau seleksi scatter (Latihan 5) memfilter tabel
@callback(Output("tbl", "data"), Output("judul-tabel", "children"),
          Input("store-data", "data"), Input("g-bar", "clickData"),
          Input("g-scatter", "selectedData"))
def update_tabel(data, click, selected):
    d = pd.DataFrame(data or [], columns=TABEL_COLS)
    judul = "Detail pelanggan (semua region terpilih)"
    if ctx.triggered_id == "g-bar" and click:
        reg = click["points"][0]["x"]
        d = d[d.region == reg]
        judul = f"Detail pelanggan — region {reg}"
    elif ctx.triggered_id == "g-scatter" and selected and selected.get("points"):
        ids = [p["customdata"][0] for p in selected["points"]]
        d = d[d.customer_id.isin(ids)]
        judul = f"Detail pelanggan — {len(d)} titik terpilih di scatter"
    return d.to_dict("records"), judul


# 5) Latihan 3: klik titik scatter -> detail pelanggan
@callback(Output("detail-pelanggan", "children"), Input("g-scatter", "clickData"),
          prevent_initial_call=True)
def tampil_detail(click):
    if not click:
        raise PreventUpdate
    cid = click["points"][0]["customdata"][0]
    r = df.loc[df.customer_id == cid].iloc[0]
    return html.Div([
        html.B(f"Pelanggan {r.customer_id}"),
        html.Ul(style={"margin": "6px 0 0 0"}, children=[
            html.Li(f"Region: {r.region}"), html.Li(f"Kontrak: {r.contract_type}"),
            html.Li(f"Keluhan: {r.num_complaints}"), html.Li(f"Status: {r.status}")]),
    ])


if __name__ == "__main__":
    app.run(debug=True, dev_tools_ui=False, port=8057)  # panel debug disembunyikan
