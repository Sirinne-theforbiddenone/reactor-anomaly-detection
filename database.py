# ==================================================
# DATABASE MODULE
# ==================================================

import sqlite3


def connect_db():

    conn = sqlite3.connect(
        "reactor.db",
        check_same_thread=False
    )

    cursor = conn.cursor()

    # ==================================================
    # REACTOR SENSOR DATA
    # ==================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reactor_data(

        time INTEGER PRIMARY KEY,

        temperature REAL,
        pressure REAL,
        flux REAL,
        coolant REAL,
        radiation REAL,

        control_rod REAL,

        status TEXT,

        scram INTEGER
    )
    """)

    # ==================================================
    # EVENT / ANOMALY LOG
    # ==================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS anomaly_log(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        time INTEGER,

        level TEXT,

        event TEXT,

        temperature REAL,
        flux REAL,
        coolant REAL,
        radiation REAL
    )
    """)

    # ==================================================
    # INDEXES
    # ==================================================

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_reactor_time
    ON reactor_data(time)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_log_time
    ON anomaly_log(time)
    """)

    conn.commit()

    return conn