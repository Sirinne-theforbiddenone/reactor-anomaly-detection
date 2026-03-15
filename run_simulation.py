#CHẠY GIẢ LẬP CẢM BIẾN VÀ LƯU DỮ LIỆU VÀO DATABASE
import time # mô phỏng thời gian thực
import os


from reactor_model import reactor_step
from database import connect_db

# reset database mỗi lần chạy
if os.path.exists("reactor.db"):
    os.remove("reactor.db")

conn = connect_db()
cursor = conn.cursor()

temp = 300
flux = 1000
coolant = 500

for t in range(2000):

    temp, pressure, flux, coolant, radiation = reactor_step(temp, flux, coolant) #tạo giá trị random

    cursor.execute(
    "INSERT INTO reactor_data VALUES (?,?,?,?,?,?)", #Lưu data vào database, mỗi lần chạy sẽ tạo ra 1 dòng mới với giá trị mới
    (t, temp, pressure, flux, coolant, radiation)
    )

    conn.commit()

    status = "NORMAL"

    if temp > 330:
        status = "WARNING"  # nếu nhiệt độ vượt quá 330 thì cảnh báo, nhưng chưa đến mức nguy hiểm

    if temp > 360:
        status = "CRITICAL" # nếu nhiệt độ vượt quá 360 thì sắp chết mẹ r

# in ra console để theo dõi, mỗi lần chạy sẽ in ra 1 dòng mới với thời gian, nhiệt độ và trạng thái hiện tại của lò phản ứng
    print(
        "time:",t,
        "temp:",round(temp,2), 
        "status:",status
    )

    if status != "NORMAL":

        cursor.execute(
        "INSERT INTO anomaly_log VALUES (?,?,?)", # nếu có bất thường thì lưu vào bảng anomaly_log, mỗi lần có bất thường sẽ tạo ra 1 dòng mới 
        (t,status,temp)
        )

        conn.commit()

    time.sleep(0.05) # để mô phỏng thời gian thực, mỗi lần chạy sẽ tạm dừng 0.05 giây trước khi chạy tiếp (mấy cái sensor thực tế cũng delay kiểu zậy)