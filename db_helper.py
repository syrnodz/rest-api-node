import sqlite3
import sys
import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "iot_sensor.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sensor_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            suhu REAL,
            kelembaban REAL,
            threshold REAL,
            alert INTEGER,
            timestamp TEXT,
            received TEXT
        )
    """)
    return conn

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Perintah tidak diberikan"}))
        return

    cmd = sys.argv[1]
    conn = get_conn()

    if cmd == "init":
        print(json.dumps({"status": "table_ready", "db": DB_PATH}))

    elif cmd == "insert":
        suhu = float(sys.argv[2])
        kelembaban = float(sys.argv[3])
        threshold = float(sys.argv[4])
        alert = int(sys.argv[5])
        timestamp = sys.argv[6] if len(sys.argv) > 6 else datetime.now().isoformat()
        received = sys.argv[7] if len(sys.argv) > 7 else datetime.now().isoformat()
        with conn:
            conn.execute(
                "INSERT INTO sensor_history (suhu, kelembaban, threshold, alert, timestamp, received) VALUES (?, ?, ?, ?, ?, ?)",
                (suhu, kelembaban, threshold, alert, timestamp, received)
            )
        print(json.dumps({"status": "inserted"}))

    elif cmd == "latest":
        row = conn.execute("SELECT * FROM sensor_history ORDER BY id DESC LIMIT 1").fetchone()
        if row:
            d = dict(row)
            d["alert"] = bool(d["alert"])
            print(json.dumps(d))
        else:
            print(json.dumps({"suhu": None, "kelembaban": None, "timestamp": None, "alert": False}))

    elif cmd == "history":
        rows = conn.execute("SELECT * FROM sensor_history ORDER BY id DESC LIMIT 50").fetchall()
        result = []
        for r in reversed(rows):
            d = dict(r)
            d["alert"] = bool(d["alert"])
            result.append(d)
        print(json.dumps(result))

    conn.close()

if __name__ == "__main__":
    main()
