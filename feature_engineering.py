# ==================================================
# FEATURE ENGINEERING MODULE
# ==================================================
#
# File này tạo ra các feature học thuật hơn
# từ dữ liệu reactor gốc.
#
# Các feature này giúp AI:
#
# - phát hiện instability
# - hiểu dynamics của reactor
# - detect abnormal transitions
#
# ==================================================

import pandas as pd


def build_features(data):

    # ==================================================
    # COPY DATAFRAME
    # ==================================================

    data = data.copy()

    # ==================================================
    # BASIC PHYSICS FEATURES
    # ==================================================

    # ------------------------------------------
    # Heat balance
    #
    # Flux cao + coolant thấp
    # => reactor nguy hiểm hơn
    # ------------------------------------------

    data["heat_balance"] = (

        data["flux"]

        /

        (data["coolant"] + 1)

    )

    # ------------------------------------------
    # Thermal stress
    #
    # Nhiệt độ và áp suất cùng tăng
    # => stress vật liệu reactor
    # ------------------------------------------

    data["thermal_stress"] = (

        data["temperature"]

        *

        data["pressure"]

    )

    # ------------------------------------------
    # Radiation efficiency
    #
    # Radiation / Flux ratio
    #
    # Nếu ratio này bất thường
    # => có thể reactor unstable
    # ------------------------------------------

    data["radiation_ratio"] = (

        data["radiation"]

        /

        (data["flux"] + 1)

    )

    # ==================================================
    # STABILITY FEATURES
    # ==================================================

    # ------------------------------------------
    # Stability index
    #
    # coolant cao + nhiệt thấp
    # => reactor ổn định hơn
    # ------------------------------------------

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

    # ------------------------------------------
    # Reactor power index
    #
    # gần giống "reactor output"
    # ------------------------------------------

    data["power_index"] = (

        data["flux"]

        *

        data["temperature"]

    ) / 1000

    # ==================================================
    # TIME SERIES FEATURES
    # ==================================================

    # ------------------------------------------
    # temperature derivative
    # ------------------------------------------

    data["temp_change"] = (

        data["temperature"].diff()

    )

    # ------------------------------------------
    # flux derivative
    # ------------------------------------------

    data["flux_change"] = (

        data["flux"].diff()

    )

    # ------------------------------------------
    # radiation derivative
    # ------------------------------------------

    data["radiation_change"] = (

        data["radiation"].diff()

    )

    # ------------------------------------------
    # coolant derivative
    # ------------------------------------------

    data["coolant_change"] = (

        data["coolant"].diff()

    )

    # ==================================================
    # ROLLING FEATURES
    # ==================================================

    # moving average temperature

    data["temp_rolling_mean"] = (

        data["temperature"]

        .rolling(window=10)

        .mean()

    )

    # moving average flux

    data["flux_rolling_mean"] = (

        data["flux"]

        .rolling(window=10)

        .mean()

    )

    # rolling standard deviation

    data["temp_rolling_std"] = (

        data["temperature"]

        .rolling(window=10)

        .std()

    )

    # ==================================================
    # CLEAN NaN
    # ==================================================

    data = data.fillna(0)

    return data