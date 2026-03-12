import sqlite3
from datetime import datetime, timezone

DB_PATH = "skuldop.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                text       TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


def save_entry(text: str):
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO entries (text, created_at) VALUES (?, ?)",
            (text, created_at),
        )
    print(f"[db] 保存: {text!r} @ {created_at}")
