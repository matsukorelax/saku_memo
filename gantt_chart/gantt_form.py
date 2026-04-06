import tkinter as tk
from gantt_chart.gantt_db import initialize, save_tasks, get_tasks
from gantt_chart.gantt_renderer import build_ascii_chart
from n8n import notify_gantt

BG     = "#1e1e1e"
FG     = "#ffffff"
ENTRY_BG = "#2d2d2d"


def _label(parent, text):
    return tk.Label(parent, text=text, bg=BG, fg=FG, anchor="w")


def _entry(parent, default=""):
    e = tk.Entry(parent, bg=ENTRY_BG, fg=FG, insertbackground=FG, relief="flat", bd=6)
    e.insert(0, default)
    return e


def show_gantt_form(root):
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel) and getattr(widget, "_is_gantt", False):
            widget.destroy()
            return

    initialize()

    win = tk.Toplevel(root)
    win._is_gantt = True
    win.title("ガントチャート - タスク登録")
    win.configure(bg=BG)
    win.attributes("-topmost", True)
    win.resizable(False, False)

    pad = {"padx": 12, "pady": 4}

    fields = [
        ("タスク名",   "task_name",  ""),
        ("開始日",     "start_date", ""),
        ("終了予定日", "end_date",   ""),
        ("進捗",       "status",     "未着手"),
    ]
    entry_vars = {}
    for label_text, key, default in fields:
        _label(win, label_text).pack(fill="x", **pad)
        e = _entry(win, default)
        e.pack(fill="x", **pad)
        entry_vars[key] = e

    def on_submit():
        name   = entry_vars["task_name"].get().strip()
        start  = entry_vars["start_date"].get().strip() or None
        end    = entry_vars["end_date"].get().strip()
        status = entry_vars["status"].get().strip() or "未着手"
        if name and end:
            save_tasks(name=name, end_date=end, start_date=start, status=status)
            chart = build_ascii_chart(get_tasks())
            notify_gantt(chart)
            win.destroy()

    tk.Button(
        win, text="登録", command=on_submit,
        bg="#444", fg=FG, relief="flat", bd=0, padx=12, pady=6
    ).pack(pady=12)
