# AI Reactor Monitoring System

Hệ thống mô phỏng giám sát lò phản ứng hạt nhân sử dụng AI để phát hiện bất thường trong dữ liệu cảm biến theo thời gian thực.

## Tính năng chính

- Mô phỏng hoạt động của lò phản ứng hạt nhân
- Sinh dữ liệu cảm biến theo thời gian thực
- Mô phỏng lỗi:
  - Quá nhiệt (Overheating)
  - Mất nước làm mát (Coolant Failure)
  - Flux instability
  - Radiation spike
- AI Anomaly Detection bằng Isolation Forest
- Feature Engineering cho dữ liệu cảm biến
- Stability Index và Health Score
- Dashboard realtime bằng Streamlit
- Root Cause Analysis
- Event Timeline Monitoring
- SQLite database để lưu dữ liệu và log sự kiện

---

# Công nghệ sử dụng

- Python
- SQLite
- Streamlit
- Scikit-learn
- Isolation Forest
- Pandas
- Matplotlib

---

# Cấu trúc project

```text
project/
│
├── dashboard.py
├── run_simulation.py
├── reactor_model.py
├── train_model.py
├── anomaly_detector.py
├── feature_engineering.py
├── database.py
├── requirements.txt
├── reactor.db
├── model.pkl
├── scaler.pkl
└── README.md
```

## Các bước chạy chương trình
# Download python
https://www.python.org/downloads/

# Các bước sau đây thực hiện trên terminal của hệ điều hành
# Cài đặt thư viện
pip install -r requirements.txt

# Chạy mô phỏng dữ liệu
python run_simulation.py
Nên chạy simulator khoảng 30–60 giây để tạo dữ liệu trước khi train model.

# Dừng simulator
Ctrl + C

# Train AI model
python train_model.py

# Chạy dashboard
streamlit run dashboard.py

## Workflow hệ thống
Simulator
    ↓
SQLite Database
    ↓
Feature Engineering
    ↓
AI Anomaly Detection
    ↓
Realtime Dashboard