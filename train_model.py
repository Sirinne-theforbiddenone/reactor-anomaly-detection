# FILE NÀY ĐỂ TRAIN CÁI MODEL Ở FILE anomaly_detector.py
import pandas as pd
import sqlite3
from sklearn.ensemble import IsolationForest
import joblib

conn = sqlite3.connect("reactor.db")

data = pd.read_sql_query(
"SELECT temperature, pressure, flux, coolant, radiation FROM reactor_data", #truy vấn dữ liệu từ bảng reactor_data trong database
conn
)

data = data[data["temperature"] < 330]

if data.empty:
    print("Database have no data. Please run the reactor simulation first.") # chưa có dữ liệu thì dừng code
    exit()

print("Training samples:", len(data))

# train model
model = IsolationForest(contamination=0.02)

model.fit(data)

# lưu model
joblib.dump(model, "model.pkl")

print("Model trained and saved!")
