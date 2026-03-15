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

model = joblib.load("model.pkl")

# =========================
# CONNECT DATABASE (READ ONLY)
# =========================

conn = sqlite3.connect(
    "file:reactor.db?mode=ro",
    uri=True,
    check_same_thread=False,
    timeout=10
)

# =========================
# LOAD DATA
# =========================

data = pd.read_sql_query(
    """
    SELECT temperature, pressure, flux, coolant, radiation
    FROM reactor_data
    ORDER BY time DESC
    LIMIT 200
    """,
    conn
)

data = data[::-1].reset_index(drop=True)

# =========================
# FEATURES FOR MODEL
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
data["anomaly"] = prediction

score = model.decision_function(features)
data["score"] = score

# =========================
# STATUS USING RECENT DATA
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
# FIND ANOMALY CAUSE
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
    "temperature": "Reactor overheating",
    "flux": "Neutron flux spike",
    "coolant": "Coolant instability",
    "pressure": "Pressure fluctuation",
    "radiation": "Radiation anomaly"
}

latest = data.iloc[-1]

if latest["anomaly"] == -1:

    causes = detect_cause(latest)

    if causes:

        for c in causes:
            st.warning("Possible cause: " + fault_map.get(c, c))

    else:
        st.info("AI detected unusual parameter combination")

# =========================
# HIGHLIGHT TABLE
# =========================

st.subheader("Latest Data")

def highlight(row):

    if row["anomaly"] == -1:
        return ["background-color: red"] * len(row)

    return [""] * len(row)

st.dataframe(data.style.apply(highlight, axis=1))

# =========================
# SENSOR CHART FUNCTION
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

    ax.set_xlabel("Time Step")
    ax.set_ylabel(sensor)

    ax.legend()

    st.pyplot(fig)

# =========================
# SENSOR MONITORING
# =========================

st.subheader("Sensor Monitoring")

plot_sensor("temperature")
plot_sensor("pressure")
plot_sensor("flux")
plot_sensor("coolant")
plot_sensor("radiation")

# =========================
# ANOMALY SCORE
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

ax.set_xlabel("Time Step")
ax.set_ylabel("Anomaly Score")

ax.legend()

st.pyplot(fig)