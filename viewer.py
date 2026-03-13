import tkinter as tk
from tkinter import ttk
from db import get_entries


def show_viewer(root):
    """メモ一覧ウィンドウを表示する。既に開いていれば閉じる（トグル）。"""
    # 既に開いていれば閉じる
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel) and getattr(widget, "_is_viewer", False):
            widget.destroy()
            return

    win = tk.Toplevel(root)
    win._is_viewer = True
    win.title("オペレーションスクルド - メモ一覧")
    win.geometry("700x400")
    win.configure(bg="#1e1e1e")
    win.attributes("-topmost", True)

    # テーブル
    columns = ("status", "text", "created_at")
    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.heading("status",     text="状態")
    tree.heading("text",       text="メモ")
    tree.heading("created_at", text="日時")
    tree.column("status",     width=60,  anchor="center")
    tree.column("text",       width=460)
    tree.column("created_at", width=160, anchor="center")

    # スクロールバー
    scrollbar = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 閉じるボタン
    close_btn = tk.Button(
        win,
        text="閉じる",
        command=win.destroy,
        bg="#3a3a3a",
        fg="#ffffff",
        relief="flat",
        padx=12,
        pady=4,
    )
    close_btn.pack(side="bottom", pady=8)

    # データ読み込み
    for entry in get_entries():
        tree.insert("", "end", values=(
            entry["status"],
            entry["text"],
            entry["created_at"],
        ))
