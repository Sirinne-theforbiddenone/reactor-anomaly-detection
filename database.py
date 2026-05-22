# FILE NÀY LÀ DATABASE ĐỂ LƯU TRỮ DỮ LIỆU VÀ LOG CỦA LÒ PHẢN ỨNG HẠT NHÂN
import sqlite3

def connect_db():

    conn = sqlite3.connect(
        "reactor.db",
        check_same_thread=False
    )

    cursor = conn.cursor()

    # =========================
    # REACTOR SENSOR DATA
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reactor_data(

        time INTEGER,

        temperature REAL,
        pressure REAL,
        flux REAL,
        coolant REAL,
        radiation REAL,
        control_rod REAL

    )
    """)

    # =========================
    # ANOMALY / EVENT LOG
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS anomaly_log(

        time INTEGER,
        level TEXT,
        event TEXT,
        temperature REAL

    )
    """)

    conn.commit()

    return conn