import joblib
import pandas as pd

from feature_engineering import build_features

class AnomalyDetector:

    def __init__(self):

        self.model = joblib.load("model.pkl")

        self.scaler = joblib.load("scaler.pkl")

    def predict(self, data):

        # dataframe copy
        data = data.copy()

        # feature engineering
        data = build_features(data)

        # select features
        features = data[[

            "temperature",
            "pressure",
            "flux",
            "coolant",
            "radiation",
            "control_rod",

            "heat_balance",
            "thermal_stress",

            "temp_change",
            "flux_change",
            "radiation_change"

        ]]

        # scaling
        scaled = self.scaler.transform(features)

        # prediction
        prediction = self.model.predict(scaled)

        score = self.model.decision_function(scaled)

        return prediction, score