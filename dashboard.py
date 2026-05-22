# ==================================================
# AI REACTOR MONITORING DASHBOARD
# ==================================================

import sqlite3

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from streamlit_autorefresh import st_autorefresh

from anomaly_detector import AnomalyDetector
from feature_engineering import build_features


# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(

    page_title="AI Reactor Monitoring",

    layout="wide"

)


# ==================================================
# AUTO REFRESH
# ==================================================

st_autorefresh(

    interval=3000,

    key="reactor_refresh"

)


# ==================================================
# CUSTOM STYLE
# ==================================================

st.markdown(
    """
    <style>

    .metric-card {

        background-color: #111111;

        border-radius: 12px;

        padding: 10px;

        border: 1px solid #333333;

    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# TITLE
# ==================================================

st.title("AI Nuclear Reactor Monitoring System")

st.markdown("""
Real-time monitoring and AI-based anomaly detection
for a simulated nuclear reactor environment.
""")


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("Control Panel")

selected_window = st.sidebar.slider(

    "Chart Window",

    min_value=50,
    max_value=1000,

    value=300,

    step=50

)

selected_sensor = st.sidebar.selectbox(

    "Focused Sensor",

    [

        "temperature",
        "pressure",
        "flux",
        "coolant",
        "radiation",
        "control_rod",

        "heat_balance",
        "thermal_stress",
        "stability_index",

        "temp_change",
        "flux_change",
        "coolant_change",

        "temp_volatility",
        "flux_volatility"

    ]

)

show_only_anomaly = st.sidebar.checkbox(

    "Show anomaly only",

    value=False

)

show_raw_scores = st.sidebar.checkbox(

    "Show raw AI score",

    value=True

)


# ==================================================
# LOAD AI MODEL
# ==================================================

try:

    detector = AnomalyDetector()

except Exception as e:

    st.error(
        "Cannot load AI model.\n"
        "Run train_model.py first."
    )

    st.stop()


# ==================================================
# DATABASE CONNECTION
# ==================================================

try:

    conn = sqlite3.connect(

        "file:reactor.db?mode=ro",

        uri=True,

        check_same_thread=False

    )

except:

    st.error("Database connection failed")

    st.stop()


# ==================================================
# LOAD DATA
# ==================================================

try:

    data = pd.read_sql_query(

        f"""
        SELECT *
        FROM reactor_data
        ORDER BY time DESC
        LIMIT {selected_window}
        """,

        conn

    )

except:

    st.warning("Waiting for simulator data...")

    st.stop()


# ==================================================
# VALIDATION
# ==================================================

if len(data) < 30:

    st.warning("Not enough data yet")

    st.stop()


# ==================================================
# REVERSE TIMELINE
# ==================================================

data = data[::-1].reset_index(drop=True)


# ==================================================
# FEATURE ENGINEERING
# ==================================================

data = build_features(data)


# ==================================================
# AI PREDICTION
# ==================================================

prediction, score = detector.predict(data)

data["anomaly"] = prediction

data["score"] = score


# ==================================================
# STICKY ANOMALY FILTER
# ==================================================
#
# giúp giảm spam anomaly
#
# chỉ coi là anomaly nếu:
# - AI score thấp mạnh
# - hoặc xuất hiện liên tục
#
# ==================================================

data["filtered_anomaly"] = 1

data.loc[data["score"] < -0.10, "filtered_anomaly"] = -1

rolling_anomaly = (

    (data["anomaly"] == -1)

    .rolling(5)

    .sum()

)

data.loc[rolling_anomaly >= 4, "filtered_anomaly"] = -1


# ==================================================
# LATEST VALUES
# ==================================================

latest = data.iloc[-1]

prev = data.iloc[-2]

temp = latest["temperature"]

pressure = latest["pressure"]

flux = latest["flux"]

coolant = latest["coolant"]

radiation = latest["radiation"]

control_rod = latest["control_rod"]

stability = latest["stability_index"]

latest_score = latest["score"]

scram = latest.get("scram", 0)


# ==================================================
# HEALTH SCORE
# ==================================================

health_score = 100

health_score -= abs(temp - 300) * 0.08

health_score -= abs(flux - 1000) * 0.015

health_score -= abs(coolant - 500) * 0.03

health_score -= abs(radiation - 50) * 0.10

health_score += latest_score * 30

health_score = max(0, min(100, health_score))


# ==================================================
# ANOMALY ANALYSIS
# ==================================================

recent_anomaly_count = len(

    data.tail(30)[
        data.tail(30)["filtered_anomaly"] == -1
    ]

)

anomaly_ratio = (

    recent_anomaly_count

    / 30

)


# ==================================================
# GLOBAL STATUS
# ==================================================

st.subheader("Reactor Status")

if scram == 1:

    st.error(
        "EMERGENCY SCRAM ACTIVATED"
    )

elif (

    temp > 390
    or radiation > 120
    or anomaly_ratio > 0.60

):

    st.error(
        "CRITICAL REACTOR CONDITION"
    )

elif (

    temp > 340
    or coolant < 430
    or flux > 1120
    or anomaly_ratio > 0.25

):

    st.warning(
        "WARNING: Reactor instability detected"
    )

else:

    st.success(
        "NORMAL: Reactor stable"
    )


# ==================================================
# HEALTH DISPLAY
# ==================================================

st.subheader("Reactor Health")

st.progress(int(health_score))

st.write(
    f"Health Score: {health_score:.2f}/100"
)


# ==================================================
# AI STATUS
# ==================================================

st.subheader("AI Monitoring Statistics")

a1, a2, a3, a4 = st.columns(4)

a1.metric(

    "AI Score",

    f"{latest_score:.4f}"

)

a2.metric(

    "Recent Anomalies",

    recent_anomaly_count

)

a3.metric(

    "Anomaly Ratio",

    f"{anomaly_ratio:.2f}"

)

a4.metric(

    "SCRAM",

    "YES" if scram == 1 else "NO"

)


# ==================================================
# LIVE METRICS
# ==================================================

st.subheader("Live Reactor Metrics")

c1, c2, c3, c4 = st.columns(4)

c1.metric(

    "Temperature",

    f"{temp:.2f} °C",

    f"{temp - prev['temperature']:.2f}"

)

c2.metric(

    "Pressure",

    f"{pressure:.2f} MPa",

    f"{pressure - prev['pressure']:.2f}"

)

c3.metric(

    "Flux",

    f"{flux:.2f}",

    f"{flux - prev['flux']:.2f}"

)

c4.metric(

    "Coolant",

    f"{coolant:.2f}",

    f"{coolant - prev['coolant']:.2f}"

)

c5, c6, c7 = st.columns(3)

c5.metric(

    "Radiation",

    f"{radiation:.2f}",

    f"{radiation - prev['radiation']:.2f}"

)

c6.metric(

    "Control Rod",

    f"{control_rod:.2f} %",

    f"{control_rod - prev['control_rod']:.2f}"

)

c7.metric(

    "Stability Index",

    f"{stability:.3f}"

)


# ==================================================
# ROOT CAUSE ANALYSIS
# ==================================================

st.subheader("Root Cause Analysis")

causes = []

if coolant < 430:

    causes.append(
        "Coolant system degradation"
    )

if flux > 1120:

    causes.append(
        "Neutron flux instability"
    )

if temp > 360:

    causes.append(
        "Core overheating"
    )

if radiation > 120:

    causes.append(
        "Radiation instability"
    )

if control_rod > 85:

    causes.append(
        "Emergency rod insertion"
    )

if latest_score < -0.10:

    causes.append(
        "AI detected abnormal operating pattern"
    )

if stability < 1.15:

    causes.append(
        "Low reactor stability"
    )

if coolant < 430 and temp > 350:

    causes.append(
        "Possible LOCA scenario"
    )

if scram == 1:

    causes.append(
        "Automatic reactor shutdown triggered"
    )

if len(causes) > 0:

    for c in causes:

        st.warning(c)

else:

    st.info(
        "No abnormal reactor behavior detected"
    )


# ==================================================
# EVENT CLASSIFICATION
# ==================================================

def classify_event(row):

    if row.get("scram", 0) == 1:

        return "SCRAM"

    if row["temperature"] > 360:

        return "Overheating"

    if row["coolant"] < 430:

        return "Coolant Failure"

    if row["flux"] > 1120:

        return "Flux Spike"

    if row["radiation"] > 120:

        return "Radiation Spike"

    return "Normal"


data["event"] = data.apply(

    classify_event,

    axis=1

)


# ==================================================
# EVENT TIMELINE
# ==================================================

st.subheader("Event Timeline")

events = data[
    data["event"] != "Normal"
]

if len(events) > 0:

    st.dataframe(

        events[[

            "time",

            "temperature",
            "pressure",
            "flux",
            "coolant",
            "radiation",

            "event"

        ]].tail(20)

    )

else:

    st.info(
        "No abnormal events detected"
    )


# ==================================================
# FOCUSED SENSOR ANALYSIS
# ==================================================

st.subheader("Focused Sensor Analysis")

fig, ax = plt.subplots(

    figsize=(14, 5)

)

ax.plot(

    data[selected_sensor],

    linewidth=2,

    label=selected_sensor

)

rolling_avg = (

    data[selected_sensor]

    .rolling(10)

    .mean()

)

ax.plot(

    rolling_avg,

    linestyle="--",

    linewidth=2,

    label="Rolling Average"

)

# filtered anomaly points

anomaly_points = data[
    data["filtered_anomaly"] == -1
]

ax.scatter(

    anomaly_points.index,

    anomaly_points[selected_sensor],

    color="red",

    label="Anomaly"

)

# scram markers

scram_points = data[
    data["scram"] == 1
]

if len(scram_points) > 0:

    ax.scatter(

        scram_points.index,

        scram_points[selected_sensor],

        color="black",

        s=90,

        label="SCRAM"

    )

ax.set_title(selected_sensor)

ax.set_xlabel("Time")

ax.set_ylabel(selected_sensor)

ax.legend()

st.pyplot(fig)


# ==================================================
# MULTI SENSOR MONITORING
# ==================================================

st.subheader("Multi-Sensor Monitoring")

sensor_list = [

    "temperature",
    "pressure",
    "flux",
    "coolant",
    "radiation",
    "control_rod"

]

for sensor in sensor_list:

    fig, ax = plt.subplots(

        figsize=(12, 3)

    )

    ax.plot(

        data[sensor],

        linewidth=2

    )

    anomaly_points = data[
        data["filtered_anomaly"] == -1
    ]

    ax.scatter(

        anomaly_points.index,

        anomaly_points[sensor],

        color="red"

    )

    ax.set_title(sensor)

    st.pyplot(fig)


# ==================================================
# AI SCORE CHART
# ==================================================

if show_raw_scores:

    st.subheader("AI Anomaly Score")

    fig, ax = plt.subplots(

        figsize=(14, 4)

    )

    ax.plot(

        data["score"],

        linewidth=2

    )

    ax.axhline(

        y=0,

        linestyle="--",

        color="red",

        label="Decision Boundary"

    )

    anomaly_points = data[
        data["filtered_anomaly"] == -1
    ]

    ax.scatter(

        anomaly_points.index,

        anomaly_points["score"],

        color="red",

        label="Anomaly"

    )

    ax.set_xlabel("Time")

    ax.set_ylabel(
        "Isolation Forest Score"
    )

    ax.legend()

    st.pyplot(fig)


# ==================================================
# ANOMALY STATISTICS
# ==================================================

st.subheader("Anomaly Statistics")

total_points = len(data)

anomaly_count = len(

    data[
        data["filtered_anomaly"] == -1
    ]

)

normal_count = (

    total_points

    - anomaly_count

)

s1, s2, s3 = st.columns(3)

s1.metric(

    "Total Samples",

    total_points

)

s2.metric(

    "Filtered Anomalies",

    anomaly_count

)

s3.metric(

    "Normal Samples",

    normal_count

)


# ==================================================
# DATA TABLE
# ==================================================

st.subheader("Latest Reactor Data")

display_data = data.copy()

if show_only_anomaly:

    display_data = display_data[
        display_data["filtered_anomaly"] == -1
    ]


def highlight(row):

    if row["filtered_anomaly"] == -1:

        return (

            ["background-color: #ffcccc"]

            * len(row)

        )

    return [""] * len(row)


st.dataframe(

    display_data.tail(30).style.apply(

        highlight,

        axis=1

    )

)