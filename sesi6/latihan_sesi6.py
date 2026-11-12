# sesi6/latihan_sesi6.py — Latihan Mandiri Sesi 6 (chart Plotly di aplikasi Dash)
# Jalankan: python sesi6/latihan_sesi6.py  lalu buka http://127.0.0.1:8051
# 1. Bar horizontal churn rate per payment_method, terurut tertinggi, + add_vline rata-rata nasional
# 2. Bubble chart: scatter dengan size="support_calls"
# 3. Sunburst region -> segmen -> kontrak (values = jumlah pelanggan) + cara membacanya
# 4. Gauge go.Indicator(mode="gauge+number") churn rate keseluruhan
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "customer_churn.csv", parse_dates=["signup_date"])
df["status"] = df["churn"].map({0: "Bertahan", 1: "Churn"})
STATUS = {"Bertahan": "#2a78d6", "Churn": "#eb6834"}
KATEGORI = ["#2a78d6", "#1baf7a", "#eda100", "#4a3aa7", "#e87ba4"]
rata2 = df.churn.mean()

# 1. Bar horizontal terurut (tertinggi di atas) + garis rata-rata
pm = df.groupby("payment_method", as_index=False)["churn"].mean().sort_values("churn")
f1 = px.bar(pm, x="churn", y="payment_method", orientation="h", text_auto=".1%",
            color_discrete_sequence=["#eb6834"],
            labels={"churn": "Churn rate", "payment_method": ""},
            title="Transfer Bank memiliki churn rate tertinggi")
f1.add_vline(x=rata2, line_dash="dot", annotation_text=f"rata-rata nasional {rata2:.1%}",
             annotation_position="top")
f1.update_xaxes(tickformat=".0%", range=[0, 0.45])

# 2. Bubble chart
f2 = px.scatter(df, x="tenure_months", y="monthly_charges", color="status", size="support_calls",
                size_max=14, opacity=0.5, color_discrete_map=STATUS, hover_name="customer_id",
                hover_data=["contract_type", "num_complaints"],
                labels={"tenure_months": "Tenure (bulan)", "monthly_charges": "Tagihan (Rp)",
                        "support_calls": "Panggilan CS", "status": "Status"},
                title="Bubble: ukuran = jumlah panggilan CS")

# 3. Sunburst tiga level
cnt = df.groupby(["region", "segment", "contract_type"]).size().reset_index(name="pelanggan")
f3 = px.sunburst(cnt, path=["region", "segment", "contract_type"], values="pelanggan",
                 color="region", color_discrete_sequence=KATEGORI,
                 title="Sunburst: region → segmen → kontrak")
f3.update_traces(insidetextorientation="radial")

# 4. Gauge
f4 = go.Figure(go.Indicator(
    mode="gauge+number", value=rata2 * 100, number={"suffix": "%", "valueformat": ".1f"},
    title={"text": "Churn rate keseluruhan"},
    gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#eb6834"},
           "steps": [{"range": [0, 30], "color": "#E6F4EA"}, {"range": [30, 60], "color": "#FDF0E6"},
                     {"range": [60, 100], "color": "#FBE3E3"}]}))

for f in (f1, f2, f3, f4):
    f.update_layout(template="plotly_white", height=420, margin=dict(t=60, l=10, r=10, b=10))

PENJELASAN = (
    "Cara membaca sunburst: lingkar dalam = region, lingkar tengah = segmen di region tersebut, "
    "lingkar luar = jenis kontrak di segmen tersebut. Luas (sudut) setiap irisan sebanding dengan "
    "jumlah pelanggan, jadi irisan Jawa yang paling lebar berarti pelanggan terbanyak. "
    "Klik sebuah irisan untuk memperbesar cabangnya; klik pusat untuk kembali."
)

app = Dash(__name__, title="Latihan Sesi 6")
app.layout = html.Div(style={"maxWidth": "1150px", "margin": "auto", "fontFamily": "Arial",
                             "padding": "0 16px"}, children=[
    html.H1("Latihan Sesi 6 — Plotly"),
    html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(420px, 1fr))",
                    "gap": "12px"}, children=[
        dcc.Graph(figure=f1), dcc.Graph(figure=f2),
        html.Div([dcc.Graph(figure=f3), html.P(PENJELASAN, style={"color": "#555"})]),
        dcc.Graph(figure=f4),
    ]),
])

if __name__ == "__main__":
    app.run(debug=True, port=8051)
