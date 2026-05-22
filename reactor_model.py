# ==================================================
# REACTOR MODEL
# ==================================================

import random


# ==================================================
# REACTOR STEP
# ==================================================

def reactor_step(state):

    # ==================================================
    # EXTRACT STATE
    # ==================================================

    temp = state["temp"]

    flux = state["flux"]

    coolant = state["coolant"]

    radiation = state["radiation"]

    control_rod = state["control_rod"]

    fault_mode = state["fault_mode"]

    fault_timer = state["fault_timer"]

    shutdown = state["shutdown"]

    tick = state["tick"]

    # ==================================================
    # AGING FACTOR
    # ==================================================

    # reactor slowly becomes unstable

    aging = tick / 5000

    # ==================================================
    # NORMAL FLUCTUATION
    # ==================================================

    flux += random.uniform(-1.0, 1.0)

    coolant += random.uniform(-0.25, 0.25)

    temp += random.uniform(-0.05, 0.05)

    # ==================================================
    # RANDOM FAULT GENERATION
    # ==================================================

    if fault_mode is None and not shutdown:

        r = random.random()

        # probability increases over time

        base = 0.0015 + aging * 0.0025

        if r < base:

            fault_mode = "COOLANT_LEAK"

            fault_timer = random.randint(40, 90)

        elif r < base + 0.0012:

            fault_mode = "NEUTRON_SPIKE"

            fault_timer = random.randint(25, 60)

        elif r < base + 0.0024:

            fault_mode = "PUMP_DEGRADATION"

            fault_timer = random.randint(50, 100)

        elif r < base + 0.0032:

            fault_mode = "PRESSURE_INSTABILITY"

            fault_timer = random.randint(30, 70)

    # ==================================================
    # FAULT DYNAMICS
    # ==================================================

    if fault_mode == "COOLANT_LEAK":

        coolant -= 1.1

        temp += 0.18

        fault_timer -= 1

    elif fault_mode == "NEUTRON_SPIKE":

        flux += 5

        temp += 0.10

        radiation += 0.05

        fault_timer -= 1

    elif fault_mode == "PUMP_DEGRADATION":

        coolant -= 0.7

        temp += 0.08

        fault_timer -= 1

    elif fault_mode == "PRESSURE_INSTABILITY":

        temp += 0.05

        radiation += 0.02

        fault_timer -= 1

    # ==================================================
    # FAULT RECOVERY
    # ==================================================

    if fault_timer <= 0:

        fault_mode = None

        fault_timer = 0

    # ==================================================
    # CASCADING EFFECTS
    # ==================================================

    if coolant < 455:

        temp += 0.05

    if coolant < 430:

        temp += 0.08

    if temp > 340:

        radiation += 0.015

    if temp > 370:

        flux += 1.0

        radiation += 0.03

    # ==================================================
    # CONTROL RODS
    # ==================================================

    flux -= control_rod * 0.045

    flux = max(930, min(flux, 1180))

    # ==================================================
    # THERMAL PHYSICS
    # ==================================================

    reactor_power = (flux - 950) / 100

    heat_generated = reactor_power * 0.15

    cooling_strength = (coolant - 470) / 55

    heat_removed = cooling_strength * 0.14

    temp += (heat_generated - heat_removed)

    # thermal inertia

    temp += (300 - temp) * 0.018

    # ==================================================
    # PRESSURE MODEL
    # ==================================================

    pressure = 15 + (temp - 300) * 0.018

    pressure += (flux - 1000) * 0.0015

    pressure = max(10, min(pressure, 30))

    # ==================================================
    # RADIATION MODEL
    # ==================================================

    radiation += (flux - 1000) * 0.0002

    radiation += random.uniform(-0.02, 0.02)

    radiation *= 0.9988

    radiation = max(45, min(radiation, 150))

    # ==================================================
    # AUTOMATIC CONTROL SYSTEM
    # ==================================================

    if temp > 335:

        control_rod += 0.35

    elif temp < 305:

        control_rod -= 0.12

    if radiation > 105:

        control_rod += 0.2

    control_rod = max(0, min(control_rod, 100))

    # ==================================================
    # NEGATIVE FEEDBACK
    # ==================================================

    if temp > 360:

        flux *= 0.999

    # ==================================================
    # SYSTEM RECOVERY
    # ==================================================

    coolant += (500 - coolant) * 0.004

    flux += (1000 - flux) * 0.0025

    radiation += (50 - radiation) * 0.0012

    # ==================================================
    # LATE GAME DETERIORATION
    # ==================================================

    if tick > 4200:

        temp += 0.015

        radiation += 0.01

    if tick > 4700:

        temp += 0.03

        radiation += 0.015

    # ==================================================
    # SCRAM CONDITIONS
    # ==================================================

    if (

        temp > 445
        or radiation > 132
        or pressure > 28

    ):

        shutdown = True

    # forced endgame scram

    if tick > 4900 and temp > 390:

        shutdown = True

    # ==================================================
    # SCRAM RESPONSE
    # ==================================================

    if shutdown:

        control_rod = 100

        flux *= 0.92

        coolant += 2

        temp -= 0.5

        radiation *= 0.996

    # ==================================================
    # SAFETY CLAMPS
    # ==================================================

    coolant = max(350, min(coolant, 550))

    temp = max(250, min(temp, 520))

    # ==================================================
    # SENSOR NOISE
    # ==================================================

    measured_temp = temp + random.uniform(-0.15, 0.15)

    measured_pressure = pressure + random.uniform(-0.03, 0.03)

    measured_flux = flux + random.uniform(-1.0, 1.0)

    measured_coolant = coolant + random.uniform(-0.4, 0.4)

    measured_radiation = radiation + random.uniform(-0.03, 0.03)

    # ==================================================
    # UPDATE STATE
    # ==================================================

    state["temp"] = temp

    state["flux"] = flux

    state["coolant"] = coolant

    state["radiation"] = radiation

    state["control_rod"] = control_rod

    state["fault_mode"] = fault_mode

    state["fault_timer"] = fault_timer

    state["shutdown"] = shutdown

    state["tick"] += 1

    # ==================================================
    # RETURN
    # ==================================================

    return {

        "temperature": measured_temp,

        "pressure": measured_pressure,

        "flux": measured_flux,

        "coolant": measured_coolant,

        "radiation": measured_radiation,

        "control_rod": control_rod,

        "shutdown": shutdown,

        "fault_mode": fault_mode

    }