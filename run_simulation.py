import time
import os
import random

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
# INITIAL VALUES
# =========================
temp = 300
flux = 1000
coolant = 500

# =========================
# SIMULATION LOOP
# =========================
for t in range(2000):

    temp, pressure, flux, coolant, radiation = reactor_step(temp, flux, coolant)

    # =========================
    # 🔥 FIX DRIFT (QUAN TRỌNG)
    # =========================
    # kéo về trạng thái bình thường nhẹ nhàng

    temp += (300 - temp) * 0.02
    flux += (1000 - flux) * 0.02
    coolant += (500 - coolant) * 0.02

    # thêm noise nhỏ
    temp += random.uniform(-0.5, 0.5)
    flux += random.uniform(-2, 2)
    coolant += random.uniform(-1, 1)

    # =========================
    # SAVE DATA
    # =========================
    cursor.execute(
        "INSERT INTO reactor_data VALUES (?,?,?,?,?,?)",
        (t, temp, pressure, flux, coolant, radiation)
    )

    conn.commit()

    # =========================
    # STATUS LOGIC
    # =========================
    status = "NORMAL"

    if temp > 330:
        status = "WARNING"

    if temp > 360:
        status = "CRITICAL"

    print(
        "time:", t,
        "temp:", round(temp, 2),
        "status:", status
    )

    # =========================
    # LOG ANOMALY
    # =========================
    if status != "NORMAL":
        cursor.execute(
            "INSERT INTO anomaly_log VALUES (?,?,?)",
            (t, status, temp)
        )
        conn.commit()

    time.sleep(0.05)