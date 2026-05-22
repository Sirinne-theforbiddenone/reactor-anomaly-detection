# ==================================================
# TRAIN ANOMALY DETECTION MODEL
# ==================================================

import sqlite3
import pandas as pd
import joblib

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from feature_engineering import build_features

# ==================================================
# LOAD DATABASE
# ==================================================

conn = sqlite3.connect("reactor.db")

data = pd.read_sql_query(

    """
    SELECT *
    FROM reactor_data
    """,

    conn

)

conn.close()

# ==================================================
# CHECK DATA
# ==================================================

if len(data) < 100:

    raise Exception(
        "Not enough reactor data to train model."
    )

# ==================================================
# FEATURE ENGINEERING
# ==================================================

data = build_features(data)

# ==================================================
# REMOVE SCRAM EVENTS
# ==================================================

data = data[
    data["scram"] == 0
]

# ==================================================
# NORMAL OPERATING REGION
# ==================================================
#
# Chỉ train bằng trạng thái gần bình thường
#
# Isolation Forest sẽ học:
# "normal reactor behavior"
#
# ==================================================

data = data[

    (data["temperature"] > 250) &
    (data["temperature"] < 360) &

    (data["pressure"] > 10) &
    (data["pressure"] < 25) &

    (data["flux"] > 850) &
    (data["flux"] < 1200) &

    (data["coolant"] > 430) &

    (data["radiation"] > 30) &
    (data["radiation"] < 120)

]

# ==================================================
# FEATURE SELECTION
# ==================================================

feature_columns = [

    # raw sensors
    "temperature",
    "pressure",
    "flux",
    "coolant",
    "radiation",
    "control_rod",

    # engineered features
    "heat_balance",
    "thermal_stress",
    "stability_index",

    # change features
    "temp_change",
    "flux_change",
    "radiation_change",
    "coolant_change",

    # rolling features
    "temp_rolling_mean",
    "flux_rolling_mean"

]

features = data[feature_columns]

# ==================================================
# SCALE FEATURES
# ==================================================

scaler = StandardScaler()

scaled_features = scaler.fit_transform(features)

# ==================================================
# TRAIN MODEL
# ==================================================

model = IsolationForest(

    n_estimators=200,

    contamination=0.02,

    random_state=42

)

model.fit(scaled_features)

# ==================================================
# SAVE MODEL
# ==================================================

joblib.dump(model, "model.pkl")

joblib.dump(scaler, "scaler.pkl")

joblib.dump(feature_columns, "feature_columns.pkl")

# ==================================================
# SUMMARY
# ==================================================

print("====================================")
print("AI Reactor Model Trained")
print("====================================")

print(f"Training samples: {len(features)}")

print(f"Feature count: {len(feature_columns)}")

print("Saved:")
print("- model.pkl")
print("- scaler.pkl")
print("- feature_columns.pkl")