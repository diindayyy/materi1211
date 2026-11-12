# models/prepare_final_model.py — MODEL PENGGANTI SEMENTARA
# ---------------------------------------------------------------------------
# Paket praktikum seharusnya berisi models/churn_model.joblib + model_metadata.json
# dari fasilitator. File itu belum ada di folder ini, jadi script ini membuat model
# pengganti dengan resep yang sama seperti Tabel P.2 buku:
#   Pipeline(imputasi median + standarisasi + one-hot) + GradientBoostingClassifier
# Angka prediksinya BISA SEDIKIT BERBEDA dari checkpoint buku (71,1%, 65 churn, dst).
# Begitu file asli dari fasilitator diterima, timpa kedua file di folder models/
# dan JANGAN jalankan script ini lagi.
#
# Jalankan sekali: python models/prepare_final_model.py
# ---------------------------------------------------------------------------
import json
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
NUM = ["tenure_months", "monthly_charges", "total_charges", "num_complaints", "support_calls"]
CAT = ["region", "segment", "contract_type", "payment_method", "internet_service"]
FEATURES = NUM + CAT

df = pd.read_csv(ROOT / "data" / "customer_churn.csv")
X, y = df[FEATURES], df["churn"]
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

pre = ColumnTransformer([
    ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), NUM),
    ("cat", OneHotEncoder(handle_unknown="ignore"), CAT),
])
model = Pipeline([("preprocess", pre), ("clf", GradientBoostingClassifier(random_state=42))])
model.fit(X_tr, y_tr)

proba = model.predict_proba(X_te)[:, 1]
metrics = {
    "roc_auc": round(roc_auc_score(y_te, proba), 4),
    "accuracy": round(accuracy_score(y_te, proba >= 0.5), 4),
    "f1": round(f1_score(y_te, proba >= 0.5), 4),
}

# Model final dilatih ulang pada seluruh data (praktik umum setelah evaluasi holdout)
model.fit(X, y)

meta = {
    "model_name": "Customer Churn Classifier",
    "model_version": "1.0.0-pengganti",
    "algorithm": "GradientBoostingClassifier (scikit-learn Pipeline)",
    "sklearn_version": sklearn.__version__,
    "note": "Model pengganti sementara; ganti dengan file dari fasilitator.",
    "feature_order": FEATURES,
    "numeric_features": NUM,
    "categorical_features": CAT,
    "categories": {c: sorted(df[c].dropna().unique().tolist()) for c in CAT},
    "numeric_ranges": {c: [float(df[c].min()), float(df[c].max())] for c in NUM},
    "decision_threshold": 0.5,
    "risk_bins": {"Rendah": [0.0, 0.3], "Sedang": [0.3, 0.6], "Tinggi": [0.6, 1.0]},
    "holdout_metrics": metrics,
}

joblib.dump(model, ROOT / "models" / "churn_model.joblib")
(ROOT / "models" / "model_metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False),
                                                    encoding="utf-8")
print("Model pengganti tersimpan. Holdout:", metrics)
