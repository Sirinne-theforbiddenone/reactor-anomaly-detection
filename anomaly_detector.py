# ==================================================
# ANOMALY DETECTOR MODULE
# ==================================================

import joblib
import numpy as np
import pandas as pd

from feature_engineering import build_features


# ==================================================
# ANOMALY DETECTOR
# ==================================================

class AnomalyDetector:

    # ==================================================
    # INIT
    # ==================================================

    def __init__(self):

        # ------------------------------------------
        # load trained model
        # ------------------------------------------

        self.model = joblib.load(
            "model.pkl"
        )

        # ------------------------------------------
        # load scaler
        # ------------------------------------------

        self.scaler = joblib.load(
            "scaler.pkl"
        )

        # ------------------------------------------
        # load feature list
        # ------------------------------------------

        self.feature_columns = joblib.load(
            "feature_columns.pkl"
        )

    # ==================================================
    # PREDICT
    # ==================================================

    def predict(self, data):

        # ==================================================
        # COPY DATAFRAME
        # ==================================================

        data = data.copy()

        # ==================================================
        # FEATURE ENGINEERING
        # ==================================================

        data = build_features(data)

        # ==================================================
        # FEATURE SELECTION
        # ==================================================

        features = data[
            self.feature_columns
        ]

        # ==================================================
        # CLEAN FEATURES
        # ==================================================

        # replace inf values
        features = features.replace(
            [np.inf, -np.inf],
            np.nan
        )

        # fill NaN
        features = features.fillna(0)

        # ==================================================
        # SCALE FEATURES
        # ==================================================

        scaled = self.scaler.transform(
            features
        )

        # ==================================================
        # RAW MODEL OUTPUT
        # ==================================================

        raw_prediction = self.model.predict(
            scaled
        )

        raw_score = self.model.decision_function(
            scaled
        )

        # ==================================================
        # SMOOTH SCORE
        # ==================================================
        #
        # giúp:
        # - giảm noise
        # - giảm anomaly spam
        # - tránh sticky anomaly
        #
        # ==================================================

        smooth_score = (

            pd.Series(raw_score)

            .rolling(
                window=5,
                min_periods=1
            )

            .mean()

        )

        # ==================================================
        # CUSTOM THRESHOLD
        # ==================================================
        #
        # Isolation Forest:
        #
        # score > 0
        #   => normal
        #
        # score < 0
        #   => anomaly
        #
        # nhưng thực tế:
        # score hơi âm vẫn có thể bình thường
        #
        # nên dùng threshold thấp hơn
        #
        # ==================================================

        anomaly_threshold = -0.03

        prediction = np.where(

            smooth_score < anomaly_threshold,

            -1,

            1

        )

        # ==================================================
        # PERSISTENCE FILTER
        # ==================================================
        #
        # anomaly phải kéo dài
        # ít nhất vài sample
        #
        # tránh:
        # - false positives
        # - spike anomaly
        #
        # ==================================================

        persistence_window = 3

        persistence = (

            pd.Series(prediction)

            .rolling(
                persistence_window,
                min_periods=1
            )

            .apply(
                lambda x: np.sum(x == -1),
                raw=True
            )

        )

        final_prediction = np.where(

            persistence >= 2,

            -1,

            1

        )

        # ==================================================
        # RETURN
        # ==================================================

        return (

            final_prediction,

            smooth_score

        )