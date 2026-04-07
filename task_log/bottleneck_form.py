import tkinter as tk
from task_log.task_db import initialize, get_tasks, add_bottleneck, get_bottlenecks
from task_log.task_renderer import build_report
from n8n import notify_bottleneck

BG     = "#1e1e1e"
FG     = "#ffffff"
ENTRY_BG = "#2d2d2d"


def show_bottleneck_form(root):
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel) and getattr(widget, "_is_bottleneck", False):
            widget.destroy()
            return

    initialize()
    tasks = get_tasks()

    win = tk.Toplevel(root)
    win._is_bottleneck = True
    win.title("ボトルネック追記")
    win.configure(bg=BG)
    win.attributes("-topmost", True)
    win.resizable(False, False)

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
        notify_bottleneck(
            task_name=task["name"],
            end_date=task["end_date"],
            ascii_chart=report,
            bottlenecks="",
        )
        win.destroy()

    tk.Button(
        win, text="追記", command=on_submit,
        bg="#444", fg=FG, relief="flat", bd=0, padx=12, pady=6
    ).pack(pady=12)
