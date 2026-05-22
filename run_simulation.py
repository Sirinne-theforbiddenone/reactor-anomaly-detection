import time
import os

from reactor_model import reactor_step
from database import connect_db

# =========================
# RESET DATABASE
# =========================

if os.path.exists("reactor.db"):
    os.remove("reactor.db")

conn = connect_db()
cursor = conn.cursor()

# =========================
# INITIAL CONDITIONS
# =========================

temp = 300
flux = 1000
coolant = 500
radiation = 50
control_rod = 30

# =========================
# SIMULATION LOOP
# =========================

for t in range(5000):

    (
        temp,
        pressure,
        flux,
        coolant,
        radiation,
        control_rod

    ) = reactor_step(
        temp,
        flux,
        coolant,
        radiation,
        control_rod
    )

    # =========================
    # REACTOR STATUS
    # =========================

    status = "NORMAL"
    event = "Stable Operation"

    if coolant < 430:
        status = "WARNING"
        event = "Coolant System Degradation"

    if flux > 1150:
        status = "WARNING"
        event = "Neutron Flux Spike"

    if temp > 360:
        status = "CRITICAL"
        event = "Core Overheating"

    if radiation > 120:
        status = "CRITICAL"
        event = "Radiation Instability"

    # =========================
    # SAVE SENSOR DATA
    # =========================

    cursor.execute(
        """
        INSERT INTO reactor_data
        VALUES (?,?,?,?,?,?,?)
        """,
        (
            t,
            temp,
            pressure,
            flux,
            coolant,
            radiation,
            control_rod
        )
    )

    # =========================
    # SAVE EVENT LOG
    # =========================

    if status != "NORMAL":

        cursor.execute(
            """
            INSERT INTO anomaly_log
            VALUES (?,?,?,?)
            """,
            (
                t,
                status,
                event,
                temp
            )
        )

    if t % 10 == 0:
        conn.commit()

    # =========================
    # CONSOLE OUTPUT
    # =========================

    print(
        f"[{t}]",
        f"Temp={temp:.2f}",
        f"Flux={flux:.2f}",
        f"Coolant={coolant:.2f}",
        f"Radiation={radiation:.2f}",
        f"Rod={control_rod:.2f}",
        f"Status={status}"
    )

    time.sleep(0.05)