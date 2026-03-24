import json
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
                created_at TEXT NOT NULL,
                status     TEXT NOT NULL DEFAULT 'open',
                file_path  TEXT,
                url        TEXT
            )
        """)
        try:
            conn.execute("ALTER TABLE entries ADD COLUMN status TEXT NOT NULL DEFAULT 'open'")
        except Exception:
            pass
        try:
            conn.execute("ALTER TABLE entries ADD COLUMN file_path TEXT")
        except Exception:
            pass
        try:
            conn.execute("ALTER TABLE entries ADD COLUMN url TEXT")
        except Exception:
            pass
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                inputs     TEXT NOT NULL,
                body       TEXT NOT NULL,
                status     TEXT NOT NULL DEFAULT 'open',
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

def get_entries() -> list[dict]:
    with get_connection() as conn:
        all_data = conn.execute(
            "SELECT id, text, created_at, status FROM entries ORDER BY created_at DESC"
        )
        rows = all_data.fetchall()

        result = []
        for row in rows:
            result.append({"id": row[0], "text": row[1], "created_at": row[2], "status":row[3]})
        return result

def update_status(entry_id: int, status: str):
    with get_connection() as conn:
        conn.execute(
            "UPDATE entries SET status = ? WHERE id = ?",
            (status, entry_id)
        )

def save_ticket(inputs: dict, body: str) -> int:
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO tickets (inputs, body, created_at) VALUES (?, ?, ?)",
            (json.dumps(inputs, ensure_ascii=False), body, created_at),
        )
        return cur.lastrowid

def get_tickets() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, inputs, body, status, created_at FROM tickets ORDER BY created_at DESC"
        ).fetchall()
    return [
        {"id": r[0], "inputs": json.loads(r[1]), "body": r[2], "status": r[3], "created_at": r[4]}
        for r in rows
    ]

def update_ticket_status(ticket_id: int, status: str):
    with get_connection() as conn:
        conn.execute(
            "UPDATE tickets SET status = ? WHERE id = ?",
            (status, ticket_id)
        )
    from n8n import notify_status
    notify_status(ticket_id, status)