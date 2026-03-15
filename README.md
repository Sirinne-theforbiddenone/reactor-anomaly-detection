# AI Reactor Monitoring System

Project này mô phỏng hệ thống AI phát hiện rủi ro của lò phản ứng hạt nhân

Tính năng:

- Mô phỏng hoạt động của lò phản ứng hạt nhân
- Tạo dữ liệu giống cảm biến của lò phản ứng hạt nhân
- Cơ sở dữ liệu SQL để lưu trữ dữ liệu
- AI phát hiện bất thường trong hoạt động
- Bảng điều khiển giám sát thời gian thực

Các bước chạy chương trình mô phỏng:

pip install -r requirements.txt

python run_simulation.py (chạy file khoảng 30 - 60 giây rồi dừng mô phỏng bằng ctrl + C)

python train_model.py

Chạy dashboard:

streamlit run dashboard.py