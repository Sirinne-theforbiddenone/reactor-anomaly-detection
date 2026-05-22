import streamlit as st
import sqlite3
import pandas as pd
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

refresh_rate = 3000

st_autorefresh(interval=refresh_rate)

# ==================================================
# CUSTOM STYLE
# ==================================================

st.markdown(
    """
    <style>

    .stMetric {
        background-color: #111111;
        border-radius: 10px;
        padding: 10px;
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
Real-time AI-assisted monitoring and anomaly detection
for a simulated nuclear reactor system.
""")

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("System Control Panel")

show_only_anomaly = st.sidebar.checkbox(
    "Show anomaly points only",
    value=False
)

selected_window = st.sidebar.slider(
    "Chart Window",
    min_value=50,
    max_value=500,
    value=200,
    step=50
)

selected_sensor = st.sidebar.selectbox(
    "Focus Sensor",
    [
        "temperature",
        "pressure",
        "flux",
        "coolant",
        "radiation",
        "control_rod",
        "heat_balance",
        "thermal_stress",
        "stability_index"
    ]
)

# ==================================================
# LOAD DETECTOR
# ==================================================

try:

    detector = AnomalyDetector()

except:

    st.error(
        "Không thể load AI model.\n\n"
        "Hãy chạy train_model.py trước."
    )

    st.stop()

# ==================================================
# CONNECT DATABASE
# ==================================================

try:

    conn = sqlite3.connect(
        "file:reactor.db?mode=ro",
        uri=True,
        check_same_thread=False
    )

except:

    st.error("Không thể kết nối database")

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

    st.warning("Đang chờ dữ liệu từ simulator...")

    st.stop()

if len(data) < 20:

    st.warning("Dữ liệu chưa đủ để phân tích")

    st.stop()

# ==================================================
# TIMELINE ORDER
# ==================================================

data = data[::-1].reset_index(drop=True)

# ==================================================
# FEATURE ENGINEERING
# ==================================================

data = build_features(data)

# ==================================================
# AI DETECTION
# ==================================================

prediction, score = detector.predict(data)

data["anomaly"] = prediction
data["score"] = score

# ==================================================
# STABILITY INDEX
# ==================================================

data["stability_index"] = (

    data["coolant"]

    /

    (
        data["temperature"]
        +
        data["radiation"]
        +
        1
    )

)

# ==================================================
# HEALTH SCORE
# ==================================================

latest = data.iloc[-1]

health_score = 100

health_score -= abs(
    latest["temperature"] - 300
) * 0.15

health_score -= abs(
    latest["flux"] - 1000
) * 0.03

health_score -= abs(
    latest["coolant"] - 500
) * 0.05

health_score = max(0, min(100, health_score))

# ==================================================
# LATEST VALUES
# ==================================================

prev = data.iloc[-2]

temp = latest["temperature"]
pressure = latest["pressure"]
flux = latest["flux"]
coolant = latest["coolant"]
radiation = latest["radiation"]
control_rod = latest["control_rod"]
stability = latest["stability_index"]

# ==================================================
# GLOBAL STATUS
# ==================================================

st.subheader("Reactor Status")

critical_conditions = (

    temp > 380 or
    radiation > 120

)

warning_conditions = (

    temp > 340 or
    coolant < 430 or
    flux > 1150

)

if critical_conditions:

    st.error(
        "CRITICAL: Reactor instability detected"
    )

elif warning_conditions:

    st.warning(
        "WARNING: Reactor operating outside safe range"
    )

else:

    st.success(
        "NORMAL: Reactor stable"
    )

# ==================================================
# HEALTH BAR
# ==================================================

st.subheader("Reactor Health Score")

st.progress(int(health_score))

st.write(
    f"Health Score: {health_score:.2f}/100"
)

# ==================================================
# LIVE METRICS
# ==================================================

st.subheader("Live Reactor Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Temperature",
    f"{temp:.2f} °C",
    f"{temp - prev['temperature']:.2f}"
)

col2.metric(
    "Pressure",
    f"{pressure:.2f} MPa",
    f"{pressure - prev['pressure']:.2f}"
)

col3.metric(
    "Flux",
    f"{flux:.2f}",
    f"{flux - prev['flux']:.2f}"
)

col4.metric(
    "Coolant",
    f"{coolant:.2f}",
    f"{coolant - prev['coolant']:.2f}"
)

col5, col6, col7 = st.columns(3)

col5.metric(
    "Radiation",
    f"{radiation:.2f}",
    f"{radiation - prev['radiation']:.2f}"
)

col6.metric(
    "Control Rod",
    f"{control_rod:.2f} %",
    f"{control_rod - prev['control_rod']:.2f}"
)

col7.metric(
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

if flux > 1150:

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

if control_rod > 80:

    causes.append(
        "Emergency control rod insertion"
    )

if stability < 1.0:

    causes.append(
        "Low reactor stability index"
    )

if coolant < 430 and temp > 350:

    causes.append(
        "Possible loss-of-coolant accident"
    )

if causes:

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

    if row["coolant"] < 430:
        return "Coolant Failure"

    if row["flux"] > 1150:
        return "Flux Spike"

    if row["temperature"] > 360:
        return "Overheating"

    if row["radiation"] > 120:
        return "Radiation Spike"

    if row["control_rod"] > 80:
        return "Emergency Shutdown"

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
# FOCUSED SENSOR CHART
# ==================================================

st.subheader("Focused Sensor Analysis")

fig, ax = plt.subplots(
    figsize=(14, 5)
)

# sensor line
ax.plot(
    data[selected_sensor],
    linewidth=2,
    label=selected_sensor
)

# rolling average
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

# anomaly points
anomaly_points = data[
    data["anomaly"] == -1
]

ax.scatter(
    anomaly_points.index,
    anomaly_points[selected_sensor],
    color="red",
    label="Anomaly"
)

# threshold lines
if selected_sensor == "temperature":

    ax.axhline(
        y=360,
        linestyle="--",
        color="orange",
        label="Warning Threshold"
    )

    ax.axhline(
        y=380,
        linestyle="--",
        color="red",
        label="Critical Threshold"
    )

if selected_sensor == "coolant":

    ax.axhline(
        y=430,
        linestyle="--",
        color="red",
        label="Low Coolant Threshold"
    )

if selected_sensor == "flux":

    ax.axhline(
        y=1150,
        linestyle="--",
        color="orange",
        label="Flux Threshold"
    )

ax.set_title(selected_sensor)

ax.set_xlabel("Time")

ax.set_ylabel(selected_sensor)

ax.legend()

st.pyplot(fig)

# ==================================================
# SENSOR MONITORING
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
        data["anomaly"] == -1
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

st.subheader("AI Anomaly Score")

fig, ax = plt.subplots(
    figsize=(14, 4)
)

ax.plot(
    data["score"],
    linewidth=2
)

# threshold line
ax.axhline(
    y=0,
    linestyle="--",
    color="red",
    label="Anomaly Boundary"
)

anomaly_points = data[
    data["anomaly"] == -1
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
    data[data["anomaly"] == -1]
)

normal_count = total_points - anomaly_count

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Samples",
    total_points
)

col2.metric(
    "Anomalies",
    anomaly_count
)

col3.metric(
    "Normal Samples",
    normal_count
)

# ==================================================
# FILTERED TABLE
# ==================================================

st.subheader("Latest Reactor Data")

display_data = data.copy()

if show_only_anomaly:

    display_data = display_data[
        display_data["anomaly"] == -1
    ]

def highlight(row):

    if row["anomaly"] == -1:

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