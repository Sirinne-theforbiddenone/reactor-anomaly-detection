import pandas as pd

def build_features(data):

    data = data.copy()

    # =========================
    # BASIC FEATURES
    # =========================

    data["heat_balance"] = (
        data["flux"] /
        (data["coolant"] + 1)
    )

    data["thermal_stress"] = (
        data["temperature"] *
        data["pressure"]
    )

    # =========================
    # TIME SERIES FEATURES
    # =========================

    data["temp_change"] = (
        data["temperature"].diff()
    )

    data["flux_change"] = (
        data["flux"].diff()
    )

    data["radiation_change"] = (
        data["radiation"].diff()
    )

    # fill NaN do diff()
    data = data.fillna(0)

    return data