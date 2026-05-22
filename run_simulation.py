# ==================================================
# RUN REACTOR SIMULATION
# ==================================================

import os
import time

from reactor_model import reactor_step
from database import connect_db


# ==================================================
# RESET DATABASE
# ==================================================

if os.path.exists("reactor.db"):

    os.remove("reactor.db")


# ==================================================
# DATABASE CONNECTION
# ==================================================

conn = connect_db()

cursor = conn.cursor()


# ==================================================
# INITIAL REACTOR STATE
# ==================================================

state = {

    # core parameters
    "temp": 300,
    "flux": 1000,
    "coolant": 500,
    "radiation": 50,
    "control_rod": 20,

    # fault system
    "fault_mode": None,
    "fault_timer": 0,

    # emergency state
    "shutdown": False,

    # reactor aging
    "tick": 0

}


# ==================================================
# STATUS CLASSIFIER
# ==================================================

def classify_status(

    temp,
    pressure,
    flux,
    coolant,
    radiation,
    shutdown

):

    # ------------------------------------------
    # SCRAM
    # ------------------------------------------

    if shutdown:

        return "SCRAM"

    # ------------------------------------------
    # CRITICAL
    # ------------------------------------------

    if (

        temp > 365
        or coolant < 435
        or radiation > 108
        or pressure > 23

    ):

        return "CRITICAL"

    # ------------------------------------------
    # WARNING
    # ------------------------------------------

    if (

        temp > 330
        or coolant < 470
        or flux > 1045
        or radiation > 85

    ):

        return "WARNING"

    # ------------------------------------------
    # NORMAL
    # ------------------------------------------

    return "NORMAL"


# ==================================================
# EVENT CLASSIFIER
# ==================================================

def classify_event(

    status,
    fault_mode

):

    # ------------------------------------------
    # fault mapping
    # ------------------------------------------

    if fault_mode == "COOLANT_LEAK":

        return "Coolant Leak"

    elif fault_mode == "NEUTRON_SPIKE":

        return "Neutron Flux Instability"

    elif fault_mode == "PUMP_DEGRADATION":

        return "Cooling Pump Degradation"

    elif fault_mode == "PRESSURE_INSTABILITY":

        return "Pressure Instability"

    # ------------------------------------------
    # status fallback
    # ------------------------------------------

    if status == "WARNING":

        return "Operational Instability"

    elif status == "CRITICAL":

        return "Critical Reactor Condition"

    elif status == "SCRAM":

        return "Emergency Reactor Shutdown"

    return "Stable Operation"


# ==================================================
# SIMULATION LOOP
# ==================================================

for t in range(5000):

    # ==================================================
    # REACTOR STEP
    # ==================================================

    data = reactor_step(state)

    temp = data["temperature"]

    pressure = data["pressure"]

    flux = data["flux"]

    coolant = data["coolant"]

    radiation = data["radiation"]

    control_rod = data["control_rod"]

    shutdown = data["shutdown"]

    fault_mode = data["fault_mode"]

    # ==================================================
    # STATUS + EVENT
    # ==================================================

    status = classify_status(

        temp,
        pressure,
        flux,
        coolant,
        radiation,
        shutdown

    )

    event = classify_event(

        status,
        fault_mode

    )

    # ==================================================
    # SAVE REACTOR DATA
    # ==================================================

    cursor.execute(
        """
        INSERT INTO reactor_data(
            time,
            temperature,
            pressure,
            flux,
            coolant,
            radiation,
            control_rod,
            status,
            scram
        )
        VALUES (?,?,?,?,?,?,?,?,?)
        """,
        (
            t,
            temp,
            pressure,
            flux,
            coolant,
            radiation,
            control_rod,
            status,
            int(shutdown)
        )
    )

    # ==================================================
    # SAVE EVENT LOG
    # ==================================================

    if status != "NORMAL":

        cursor.execute(
            """
            INSERT INTO anomaly_log(
                time,
                level,
                event,
                temperature,
                flux,
                coolant,
                radiation
            )
            VALUES (?,?,?,?,?,?,?)
            """,
            (
                t,
                status,
                event,
                temp,
                flux,
                coolant,
                radiation
            )
        )

    # ==================================================
    # PERIODIC COMMIT
    # ==================================================

    if t % 25 == 0:

        conn.commit()

    # ==================================================
    # CONSOLE OUTPUT
    # ==================================================

    print(

        f"[{t}]",

        f"TEMP={temp:.2f}",

        f"PRESSURE={pressure:.2f}",

        f"FLUX={flux:.2f}",

        f"COOLANT={coolant:.2f}",

        f"RADIATION={radiation:.2f}",

        f"ROD={control_rod:.2f}",

        f"FAULT={fault_mode}",

        f"STATUS={status}"

    )

    # ==================================================
    # SCRAM TERMINATION
    # ==================================================

    if shutdown:

        print("\n=== EMERGENCY SCRAM ACTIVATED ===")

        print("Reactor shutdown sequence initiated")

        conn.commit()

        break

    # ==================================================
    # REALTIME DELAY
    # ==================================================

    time.sleep(0.05)


# ==================================================
# CLEANUP
# ==================================================

conn.commit()

conn.close()

print("\nSimulation finished.")