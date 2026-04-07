import os
import sqlite3
from datetime import timezone, datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gantt.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                start_date  TEXT NOT NULL,
                end_date    TEXT NOT NULL,
                status      TEXT NOT NULL DEFAULT '未着手',
                is_archived INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bottlenecks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id     INTEGER NOT NULL REFERENCES tasks(id),
                content     TEXT NOT NULL,
                created_at  TEXT NOT NULL
            )
        """)


def save_tasks(name: str, end_date: str, start_date: str = None, status: str = "未着手"):
    if not start_date:
        start_date = datetime.now(timezone.utc).strftime('%m-%d')
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO tasks (name, start_date, end_date, status) VALUES (?, ?, ?, ?)",
            (name, start_date, end_date, status),
        )
    print(f"[db] タスク保存: {name!r} @ {start_date}")


def add_bottleneck(task_id: int, content: str):
    created_at = datetime.now(timezone.utc).strftime('%m-%d %H:%M')
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO bottlenecks (task_id, content, created_at) VALUES (?, ?, ?)",
            (task_id, content, created_at),
        )
    print(f"[db] ボトルネック追記: task_id={task_id}")


def get_tasks() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, start_date, end_date, status FROM tasks WHERE is_archived = 0 ORDER BY start_date DESC"    
        ).fetchall()
    return [
        {"id": r[0], "name": r[1], "start_date": r[2], "end_date": r[3], "status": r[4]}
        for r in rows
    ]


def get_bottlenecks(task_id: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, content, created_at FROM bottlenecks WHERE task_id=? ORDER BY created_at",
            (task_id,)
        ).fetchall()
    return [{"id": r[0], "content": r[1], "created_at": r[2]} for r in rows]

def archive_task(task_id: int):
    with get_connection() as conn:
        conn.execute(
            "UPDATE tasks SET is_archived = 1 WHERE id = ?",
            (task_id,)
        )
    print(f"[db] タスクアーカイブ: task_id={task_id}")

def status_update(task_id: int, status: str):
    with get_connection() as conn:
        conn.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (status, task_id)
        )
    print(f"[db] タスクステータス更新: task_id={task_id}, status={status}")
    