# FILE NÀY ĐỂ TRAIN CÁI MODEL Ở FILE anomaly_detector.py
import sqlite3
import pandas as pd
import joblib

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from feature_engineering import build_features

# =========================
# LOAD DATABASE
# =========================

conn = sqlite3.connect("reactor.db")

data = pd.read_sql_query(
    """
    SELECT *
    FROM reactor_data
    """,
    conn
)

# =========================
# FEATURE ENGINEERING
# =========================

data = build_features(data)

# =========================
# NORMAL OPERATING REGION
# =========================

data = data[

    (data["temperature"] < 330) &
    (data["flux"] < 1100) &
    (data["coolant"] > 450) &
    (data["radiation"] < 90)

]

# =========================
# TRAIN FEATURES
# =========================

features = data[[

    "temperature",
    "pressure",
    "flux",
    "coolant",
    "radiation",
    "control_rod",

    "heat_balance",
    "thermal_stress",

    "temp_change",
    "flux_change",
    "radiation_change"

]]

# =========================
# SCALE DATA
# =========================

scaler = StandardScaler()

scaled_features = scaler.fit_transform(features)

# =========================
# TRAIN MODEL
# =========================

model = IsolationForest(

    contamination=0.02,
    random_state=42

)

model.fit(scaled_features)

# =========================
# SAVE MODEL
# =========================

joblib.dump(model, "model.pkl")

joblib.dump(scaler, "scaler.pkl")

print("Model trained successfully")