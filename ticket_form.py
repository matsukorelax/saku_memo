import json
import threading
import tkinter as tk
from tkinter import ttk
from db import get_entries, save_ticket
from dify import run_ticket_helper
from n8n import notify_ticket

BG     = "#1e1e1e"
FG     = "#ffffff"
ENTRY_BG = "#2d2d2d"


def _label(parent, text):
    return tk.Label(parent, text=text, bg=BG, fg=FG, anchor="w")


def _entry(parent, default=""):
    e = tk.Entry(parent, bg=ENTRY_BG, fg=FG, insertbackground=FG, relief="flat", bd=6)
    e.insert(0, default)
    return e


def show_ticket_form(root):
    """起票ヘルパーフォームを表示する。既に開いていれば前面に出す。"""
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel) and getattr(widget, "_is_ticket", False):
            widget.destroy()
            return

    # config読み込み
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    devices = config.get("devices", {})
    envs    = config.get("envs", {})

    # 直前のメモを取得
    entries = get_entries()
    latest_memo = entries[0]["text"] if entries else ""

    win = tk.Toplevel(root)
    win._is_ticket = True
    win.title("起票ヘルパー")
    win.configure(bg=BG)
    win.attributes("-topmost", True)
    win.resizable(False, False)

    pad = {"padx": 12, "pady": 4}

    # ── テキスト入力フィールド ──
    fields = [
        ("操作ログ（要約）",  "memo_check_log",      latest_memo),
        ("確認した結果",      "memo_result",         ""),
        ("期待する結果",      "memo_expected_result",""),
        ("再現率",            "memo_rate",           ""),
        ("確認アカウント",    "memo_account",        ""),
        ("ユーザーID",        "memo_user_id",        ""),
    ]
    entry_vars = {}
    for label_text, key, default in fields:
        _label(win, label_text).pack(fill="x", **pad)
        e = _entry(win, default)
        e.pack(fill="x", **pad)
        entry_vars[key] = e

    # ── 出力形式 ──
    _label(win, "出力形式").pack(fill="x", **pad)
    output_fmt = tk.StringVar(value="QCテンプレ")
    fmt_frame = tk.Frame(win, bg=BG)
    fmt_frame.pack(fill="x", **pad)
    for fmt in ["QCテンプレ"]:
        tk.Radiobutton(
            fmt_frame, text=fmt, variable=output_fmt, value=fmt,
            bg=BG, fg=FG, selectcolor="#444", activebackground=BG
        ).pack(side="left", padx=4)

    # ── 確認端末 ──
    _label(win, "確認端末").pack(fill="x", **pad)
    device_vars = {k: tk.BooleanVar() for k in devices}
    dev_frame = tk.Frame(win, bg=BG)
    dev_frame.pack(fill="x", **pad)
    for key, label_text in devices.items():
        tk.Checkbutton(
            dev_frame, text=label_text, variable=device_vars[key],
            bg=BG, fg=FG, selectcolor="#444", activebackground=BG
        ).pack(side="left", padx=4)

    # ── 確認環境 ──
    _label(win, "確認環境").pack(fill="x", **pad)
    env_vars = {k: tk.BooleanVar() for k in envs}
    env_frame = tk.Frame(win, bg=BG)
    env_frame.pack(fill="x", **pad)
    for key, label_text in envs.items():
        tk.Checkbutton(
            env_frame, text=label_text, variable=env_vars[key],
            bg=BG, fg=FG, selectcolor="#444", activebackground=BG
        ).pack(side="left", padx=4)

    # ── 結果表示エリア ──
    _label(win, "結果").pack(fill="x", **pad)
    result_text = tk.Text(win, height=10, bg=ENTRY_BG, fg=FG, relief="flat", bd=6, state="disabled")
    result_text.pack(fill="both", expand=True, **pad)

    # ── ボタン ──
    def on_submit():
        inputs = {key: e.get() for key, e in entry_vars.items()}
        inputs["output_fmt"] = output_fmt.get()
        inputs["device_choice"] = True
        inputs["choice_field"] = True
        inputs.update({k: v.get() for k, v in device_vars.items()})
        inputs.update({k: v.get() for k, v in env_vars.items()})

        result_text.config(state="normal")
        result_text.delete("1.0", "end")
        result_text.insert("end", "送信中...")
        result_text.config(state="disabled")
        submit_btn.config(state="disabled")

        def call_dify():
            result = run_ticket_helper(inputs)
            win.after(0, lambda: show_result(result))

        def show_result(result):
            result_text.config(state="normal")
            result_text.delete("1.0", "end")
            result_text.insert("end", result)
            result_text.config(state="disabled")
            submit_btn.config(state="normal")
            ticket_id = save_ticket(inputs, result)
            notify_ticket(ticket_id, inputs, result)

        threading.Thread(target=call_dify, daemon=True).start()

    btn_frame = tk.Frame(win, bg=BG)
    btn_frame.pack(fill="x", pady=8)
    submit_btn = tk.Button(
        btn_frame, text="送信", command=on_submit,
        bg="#3a7bd5", fg=FG, relief="flat", padx=16, pady=4
    )
    submit_btn.pack(side="right", padx=12)
    tk.Button(
        btn_frame, text="閉じる", command=win.destroy,
        bg="#3a3a3a", fg=FG, relief="flat", padx=16, pady=4
    ).pack(side="right", padx=4)
