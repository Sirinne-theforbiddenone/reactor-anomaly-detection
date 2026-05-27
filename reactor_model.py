# ==================================================
# REACTOR MODEL
# ==================================================

import random


# ==================================================
# REACTOR STEP
# ==================================================

def reactor_step(state):

    # ==================================================
    # LOAD STATE
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
    # AGING
    # ==================================================

    aging = tick / 5000

    # ==================================================
    # NORMAL FLUCTUATION
    # ==================================================

    flux += random.uniform(-1.5, 1.5)

    coolant += random.uniform(-0.4, 0.4)

    temp += random.uniform(-0.08, 0.08)

    # ==================================================
    # RANDOM FAULT GENERATION
    # ==================================================

    if fault_mode is None and not shutdown:

        r = random.random()

        base = 0.002 + aging * 0.003

        if r < base:

            fault_mode = "COOLANT_LEAK"

            fault_timer = random.randint(20, 45)

        elif r < base + 0.0018:

            fault_mode = "NEUTRON_SPIKE"

            fault_timer = random.randint(12, 30)

        elif r < base + 0.0032:

            fault_mode = "PUMP_DEGRADATION"

            fault_timer = random.randint(25, 50)

        elif r < base + 0.0042:

            fault_mode = "PRESSURE_INSTABILITY"

            fault_timer = random.randint(15, 35)

    # ==================================================
    # FAULT DYNAMICS
    # ==================================================

    if fault_mode == "COOLANT_LEAK":

        coolant -= 1.8

        temp += 0.32

        radiation += 0.02

        fault_timer -= 1

    elif fault_mode == "NEUTRON_SPIKE":

        flux += 8

        temp += 0.22

        radiation += 0.08

        fault_timer -= 1

    elif fault_mode == "PUMP_DEGRADATION":

        coolant -= 1.0

        temp += 0.18

        fault_timer -= 1

    elif fault_mode == "PRESSURE_INSTABILITY":

        temp += 0.15

        radiation += 0.04

        flux += 2

        fault_timer -= 1

    # ==================================================
    # FAULT END
    # ==================================================

    if fault_timer <= 0:

        fault_mode = None

        fault_timer = 0

    # ==================================================
    # CASCADING EFFECTS
    # ==================================================

    if coolant < 465:

        temp += 0.06

    if coolant < 440:

        temp += 0.12

        radiation += 0.02

    if temp > 340:

        radiation += 0.02

    if temp > 370:

        flux += 1.5

        radiation += 0.04

    # ==================================================
    # CONTROL ROD SYSTEM
    # ==================================================

    if temp > 335:

        control_rod += 0.45

    elif temp < 305:

        control_rod -= 0.15

    if radiation > 100:

        control_rod += 0.3

    control_rod = max(0, min(control_rod, 100))

    # ==================================================
    # FLUX CONTROL
    # ==================================================

    flux -= control_rod * 0.05

    # weaker negative feedback

    if temp > 360:

        flux *= 0.9994

    # ==================================================
    # THERMAL MODEL
    # ==================================================

    reactor_power = (flux - 950) / 100

    heat_generated = reactor_power * 0.18

    cooling_strength = (coolant - 470) / 50

    heat_removed = cooling_strength * 0.13

    temp += (heat_generated - heat_removed)

    # weaker thermal inertia

    temp += (300 - temp) * 0.012

    # ==================================================
    # PRESSURE
    # ==================================================

    pressure = 15 + (temp - 300) * 0.02

    pressure += (flux - 1000) * 0.002

    pressure = max(10, min(pressure, 30))

    # ==================================================
    # RADIATION
    # ==================================================

    radiation += (flux - 1000) * 0.00025

    radiation += random.uniform(-0.03, 0.03)

    radiation *= 0.999

    # ==================================================
    # RECOVERY SYSTEM
    # ==================================================

    coolant += (500 - coolant) * 0.0035

    flux += (1000 - flux) * 0.002

    radiation += (50 - radiation) * 0.001

    # ==================================================
    # ENDGAME DETERIORATION
    # ==================================================

    if tick > 3800:

        temp += 0.015

        radiation += 0.008

    if tick > 4400:

        temp += 0.03

        radiation += 0.015

    if tick > 4800:

        temp += 0.05

        radiation += 0.03

    # ==================================================
    # SCRAM CONDITIONS
    # ==================================================

    if (

        temp > 440
        or radiation > 130
        or pressure > 28

    ):

        shutdown = True

    # forced ending

    if tick >= 4950:

        shutdown = True

    # ==================================================
    # SCRAM RESPONSE
    # ==================================================

    if shutdown:

        control_rod = 100

        flux *= 0.90

        coolant += 3

        temp -= 0.7

        radiation *= 0.995

    # ==================================================
    # LIMITS
    # ==================================================

    coolant = max(350, min(coolant, 550))

    temp = max(250, min(temp, 520))

    radiation = max(40, min(radiation, 160))

    flux = max(900, min(flux, 1250))

    # ==================================================
    # SENSOR NOISE
    # ==================================================

    measured_temp = temp + random.uniform(-0.2, 0.2)

    measured_pressure = pressure + random.uniform(-0.05, 0.05)

    measured_flux = flux + random.uniform(-1.5, 1.5)

    measured_coolant = coolant + random.uniform(-0.5, 0.5)

    measured_radiation = radiation + random.uniform(-0.05, 0.05)

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