# FILE NÀY LÀ DATABASE ĐỂ LƯU TRỮ DỮ LIỆU VÀ LOG CỦA LÒ PHẢN ỨNG HẠT NHÂN
import sqlite3

def connect_db():

    conn = sqlite3.connect("reactor.db") # Kết nối đến file database, nếu chưa có sẽ tự tạo mới
    cursor = conn.cursor()
    
    # Bảng này lưu trữ dữ liệu hoạt động của lò phản ứng theo thời gian
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reactor_data(    
        time INTEGER,
        temperature REAL,
        pressure REAL,
        flux REAL,
        coolant REAL,
        radiation REAL
    )
    """)

    # Bảng này lưu trữ log về các sự kiện bất thường được phát hiện
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS anomaly_log(  
        time INTEGER,
        level TEXT,
        temperature REAL
    )
    """)

    conn.commit() # Nhớ có commit sau khi tạo bảng để lưu thay đổi

    return conn