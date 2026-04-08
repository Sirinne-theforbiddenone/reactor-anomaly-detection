import streamlit as st
import sqlite3
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# =========================
# AUTO REFRESH
# =========================
st_autorefresh(interval=3000)

st.title("AI Nuclear Reactor Monitoring")

# =========================
# LOAD MODEL
# =========================
try:
    model = joblib.load("model.pkl")
except:
    st.error("Model chưa tồn tại! Hãy chạy train_model.py trước.")
    st.stop()

# =========================
# CONNECT DATABASE
# =========================
try:
    conn = sqlite3.connect(
        "file:reactor.db?mode=ro",
        uri=True,
        check_same_thread=False
    )
except:
    st.error("Database chưa sẵn sàng!")
    st.stop()

# =========================
# LOAD DATA
# =========================
try:
    data = pd.read_sql_query(
        """
        SELECT temperature, pressure, flux, coolant, radiation
        FROM reactor_data
        ORDER BY time DESC
        LIMIT 200
        """,
        conn
    )
except:
    st.warning("Chưa có dữ liệu từ simulator...")
    st.stop()

if len(data) < 10:
    st.warning("Dữ liệu chưa đủ để phân tích")
    st.stop()

data = data[::-1].reset_index(drop=True)

# =========================
# FEATURES
# =========================
features = data[[
    "temperature",
    "pressure",
    "flux",
    "coolant",
    "radiation"
]]

# =========================
# AI PREDICTION
# =========================
prediction = model.predict(features)
score = model.decision_function(features)

data["anomaly"] = prediction
data["score"] = score

# =========================
# STATUS
# =========================
recent = data.tail(5)

avg_temp = recent["temperature"].mean()
anomaly_count = sum(recent["anomaly"] == -1)

st.subheader("Reactor Status")

if avg_temp > 360:
    st.error("CRITICAL: Reactor overheating")

elif anomaly_count >= 3:
    st.warning("WARNING: AI detected anomaly")

else:
    st.success("NORMAL: Reactor stable")

# =========================
# ROOT CAUSE ANALYSIS
# =========================
mean_vals = features.mean()
std_vals = features.std()

def detect_cause(row):
    causes = []
    for col in features.columns:
        if abs(row[col] - mean_vals[col]) > 2 * std_vals[col]:
            causes.append(col)
    return causes

fault_map = {
    "temperature": "Overheating",
    "flux": "Flux spike",
    "coolant": "Coolant issue",
    "pressure": "Pressure issue",
    "radiation": "Radiation spike"
}

latest = data.iloc[-1]

if latest["anomaly"] == -1:
    causes = detect_cause(latest)

    if causes:
        for c in causes:
            st.warning("Cause: " + fault_map.get(c, c))
    else:
        st.info("Unknown anomaly pattern")

# =========================
# TABLE
# =========================
st.subheader("Latest Data")

def highlight(row):
    if row["anomaly"] == -1:
        return ["background-color: #ffcccc"] * len(row)
    return [""] * len(row)

st.dataframe(data.style.apply(highlight, axis=1))

# =========================
# PLOT FUNCTION
# =========================
def plot_sensor(sensor):
    fig, ax = plt.subplots()

    ax.plot(data[sensor], label=sensor)

    anomaly_points = data[data["anomaly"] == -1]

    ax.scatter(
        anomaly_points.index,
        anomaly_points[sensor],
        color="red",
        label="Anomaly"
    )

    ax.set_xlabel("Time")
    ax.set_ylabel(sensor)
    ax.legend()

    st.pyplot(fig)

# =========================
# SENSOR CHARTS
# =========================
st.subheader("Sensor Monitoring")

for sensor in features.columns:
    plot_sensor(sensor)

# =========================
# SCORE CHART
# =========================
st.subheader("AI Anomaly Score")

fig, ax = plt.subplots()

ax.plot(data["score"], label="Score")

anomaly_points = data[data["anomaly"] == -1]

ax.scatter(
    anomaly_points.index,
    anomaly_points["score"],
    color="red",
    label="Anomaly"
)

ax.legend()
st.pyplot(fig)