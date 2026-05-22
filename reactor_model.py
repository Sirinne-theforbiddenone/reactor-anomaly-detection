import random

def reactor_step(
    temp,
    flux,
    coolant,
    radiation,
    control_rod
):

    # =========================
    # NORMAL FLUCTUATION
    # =========================
    flux += random.uniform(-3, 3)
    coolant += random.uniform(-1, 1)

    # =========================
    # RANDOM FAILURE EVENTS
    # =========================

    # coolant leak
    if random.random() < 0.01:
        coolant -= random.uniform(30, 60)

    # neutron spike
    if random.random() < 0.005:
        flux += random.uniform(100, 200)

    # =========================
    # CONTROL RODS
    # =========================

    # rods absorb neutrons
    flux -= control_rod * 0.8

    # =========================
    # REACTOR PHYSICS
    # =========================

    # heat generation
    heat_generated = flux * 0.008

    # cooling system
    heat_removed = coolant * 0.015

    # thermal dynamics
    temp += (heat_generated - heat_removed)

    # =========================
    # AUTOMATIC CONTROL SYSTEM
    # =========================

    # overheating → insert rods
    if temp > 340:
        control_rod += 2

    # stable → reduce rods
    if temp < 310:
        control_rod -= 1

    # emergency shutdown
    if temp > 400:
        control_rod = 100

    # rod limits
    control_rod = max(0, min(control_rod, 100))

    # =========================
    # NEGATIVE FEEDBACK
    # =========================

    if temp > 360:
        flux *= 0.995

    # =========================
    # RADIATION MODEL
    # =========================

    radiation += flux * 0.002

    # radioactive decay
    radiation *= 0.995

    # =========================
    # PRESSURE MODEL
    # =========================

    pressure = 15 + (temp - 300) * 0.03

    # =========================
    # SYSTEM RECOVERY
    # =========================

    coolant += (500 - coolant) * 0.01
    flux += (1000 - flux) * 0.003

    # =========================
    # SENSOR NOISE
    # =========================

    measured_temp = temp + random.uniform(-0.5, 0.5)

    measured_pressure = pressure + random.uniform(-0.1, 0.1)

    measured_flux = flux + random.uniform(-5, 5)

    measured_coolant = coolant + random.uniform(-2, 2)

    measured_radiation = radiation + random.uniform(-0.5, 0.5)

    return (

        measured_temp,
        measured_pressure,
        measured_flux,
        measured_coolant,
        measured_radiation,
        control_rod

    )