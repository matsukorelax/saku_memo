import sqlite3
from datetime import timezone, datetime

DB_PATH = "gantt.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def initialize():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTs tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                start_date  TEXT NOT NULL,
                end_date    TEXT NOT NULL,
                status      TEXT NOT NULL DEFAULT '未着手',
                note        TEXT
                )
        """)
        
def save_tasks(
    name: str, end_date: str, start_date: str = None, status: str = "未着手", note: str = None
    ):
    if not start_date:
          start_date = datetime.now(timezone.utc).strftime('%m-%d')
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO tasks (name, start_date, end_date, status, note) VALUES (?, ?, ?, ?, ?)",
            (name, start_date, end_date, status, note),
        )
    print(f"[db] 保存: {name!r} @ {start_date}")


def get_tasks() -> list[dict]:
    with get_connection() as conn:
        all_data = conn.execute(
            "SELECT id, name, start_date, end_date, status, note FROM tasks ORDER BY start_date"
        )
        rows = all_data.fetchall()

        result = []
        for row in rows:
            result.append({
                "id": row[0], "name": row[1], "start_date": row[2], "end_date": row[3], "status": row[4], "note": row[5]
                })
        return result