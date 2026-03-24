import json
import threading
import tkinter as tk
from gantt_db import get_tasks

BG     = "#1e1e1e"
FG     = "#ffffff"
ENTRY_BG = "#2d2d2d"

def show_gantt_form(root):
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel) and getattr(widget, "_is_gantt", False):
            widget.destroy()
            return
    
    tasks = get_tasks()

    win = tk.Toplevel(root)
    win._is_gantt = True
    win.title("ガントチャート")
    win.configure(bg=BG)
    win.attributes("-topmost", True)
    win.resizable(False, False)

    pad = {"padx": 12, "pady": 4}

    fields = [
        ("タスク名",    "task_name",      ""),
        ("開始日",      "start_date",         ""),
        ("終了予定日",   "end_date",          ""),
        ("進捗",         "progress",           ""),
        ("ボトルネック",  "bottle_neck",        ""),
    ]
    entry_vars = {}
    for label_text, key, default in fields:
        _label(win, label_text).pack(fill="x", **pad)
        e = _entry(win, default)