import tkinter as tk
from task_log.task_db import initialize, save_tasks, get_tasks, get_bottlenecks, status_update, archive_task
from task_log.task_renderer import build_report
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


def show_task_form(root):
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel) and getattr(widget, "_is_task", False):
            widget.destroy()
            return

    initialize()

    win = tk.Toplevel(root)
    win._is_task = True
    win.title("タスク登録")
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
            tasks = get_tasks()
            bottlenecks_map = {t["id"]: get_bottlenecks(t["id"]) for t in tasks}
            report = build_report(tasks, bottlenecks_map)
            notify_gantt(report)
            win.destroy()

    tk.Button(
        win, text="登録", command=on_submit,
        bg="#444", fg=FG, relief="flat", bd=0, padx=12, pady=6
    ).pack(pady=12)

def show_task_detail(root):
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel) and getattr(widget, "_is_task_detail", False):
            widget.destroy()
            return

    initialize()
    tasks = get_tasks()

    win = tk.Toplevel(root)
    win._is_task_detail = True
    win.title("タスク詳細")
    win.configure(bg=BG)
    win.attributes("-topmost", True)

    pad = {"padx": 12, "pady": 4}

    tk.Label(win, text="タスク", bg=BG, fg=FG, anchor="w").pack(fill="x", **pad)

    task_var = tk.StringVar()
    task_map = {f"[{t['id']}] {t['name']}": t for t in tasks}
    options  = list(task_map.keys()) or ["（タスクなし）"]
    task_var.set(options[0])

    om = tk.OptionMenu(win, task_var, *options)
    om.configure(bg=ENTRY_BG, fg=FG, activebackground="#555", activeforeground=FG,
                 highlightthickness=0, relief="flat")
    om.pack(fill="x", **pad)

    tk.Label(win, text="ボトルネック内容", bg=BG, fg=FG, anchor="w").pack(fill="x", **pad)
    text_box = tk.Text(
        win, bg=ENTRY_BG, fg=FG, insertbackground=FG,
        relief="flat", bd=6, height=4, wrap="word"
    )
    text_box.pack(fill="x", **pad)

    def on_submit():
        selected = task_var.get()
        content  = text_box.get("1.0", "end").strip()
        if selected not in task_map or not content:
            return

        task    = task_map[selected]
        task_id = task["id"]

        add_bottleneck(task_id=task_id, content=content)

        tasks = get_tasks()
        bottlenecks_map = {t["id"]: get_bottlenecks(t["id"]) for t in tasks}
        report = build_report(tasks, bottlenecks_map)

        win.destroy()

    tk.Button(
        win, text="登録", command=on_submit,
        bg="#444", fg=FG, relief="flat", bd=0, padx=12, pady=6
    ).pack(pady=12)
    
    tk.Label(win, text="ステータス", bg=BG, fg=FG, anchor="w").pack(fill="x", **pad)
    status_var = tk.StringVar()
    status_var.set("未着手")
    status_menu = tk.OptionMenu(win, status_var, "未着手", "進行中", "完了", "引継ぎ済")
    status_menu.configure(bg=ENTRY_BG, fg=FG, activebackground="#555", activeforeground=FG,
                         highlightthickness=0, relief="flat")
    status_menu.pack(fill="x", **pad)

    def change_status():
        selected = task_var.get()
        if selected not in task_map:
            return

        task    = task_map[selected]
        task_id = task["id"]

        status_update(task_id=task_id, status=status_var.get())

    

    tk.Button(
        win, text="ステータス変更", command=change_status,
        bg="#444", fg=FG, relief="flat", bd=0, padx=12, pady=6
    ).pack(pady=12)

    