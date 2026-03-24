import tkinter as tk
from tkinter import ttk
from db import get_tickets, update_ticket_status

def show_ticket(root):

    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel) and getattr(widget, "_is_ticket", False):
            widget.destroy()
            return

    win = tk.Toplevel(root)
    win._is_ticket = True
    win.title("起票一覧")
    win.geometry("700x600")
    win.configure(bg="#1e1e1e")
    win.attributes("-topmost", True)

    # iid（ツリー行のキー）→ チケットID の対応表
    id_map = {}

    # 上段：ツリー
    top_frame = tk.Frame(win, bg="#1e1e1e")
    top_frame.pack(fill="both", expand=True)

    columns = ("status", "body", "created_at")
    tree = ttk.Treeview(top_frame, columns=columns, show="headings")
    tree.heading("status",     text="状態")
    tree.heading("body",       text="チケット内容")
    tree.heading("created_at", text="日時")
    tree.column("status",     width=60,  anchor="center")
    tree.column("body",       width=460)
    tree.column("created_at", width=160, anchor="center")

    # スクロールバー
    scrollbar = ttk.Scrollbar(top_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 下段：全文表示
    detail = tk.Text(win, height=8, bg="#2d2d2d", fg="#ffffff", relief="flat", bd=6, state="disabled")
    detail.pack(fill="both", padx=12, pady=4)

    def load_tickets():
        """ツリーをクリアして DB から再読み込みする。"""
        id_map.clear()
        for iid in tree.get_children():
            tree.delete(iid)
        for entry in get_tickets():
            iid = tree.insert("", "end", values=(
                entry["status"],
                entry["body"],
                entry["created_at"],
            ))
            id_map[iid] = entry["id"]

    def on_select(event):
        selected = tree.focus()
        if not selected:
            return
        body = tree.item(selected)["values"][1]
        detail.config(state="normal")
        detail.delete("1.0", "end")
        detail.insert("end", body)
        detail.config(state="disabled")

    def on_toggle_status():
        """選択中の行のステータスを open ↔ closed で切り替える。"""
        selected = tree.focus()
        if not selected:
            return
        ticket_id = id_map[selected]
        current_status = tree.item(selected)["values"][0]
        new_status = "closed" if current_status == "open" else "open"
        update_ticket_status(ticket_id, new_status)
        load_tickets()

    tree.bind("<<TreeviewSelect>>", on_select)

    # ボタン行
    btn_frame = tk.Frame(win, bg="#1e1e1e")
    btn_frame.pack(side="bottom", fill="x", pady=8)

    tk.Button(
        btn_frame, text="Open/Closed 切替", command=on_toggle_status,
        bg="#3a7bd5", fg="#ffffff", relief="flat", padx=12, pady=4,
    ).pack(side="left", padx=12)

    tk.Button(
        btn_frame, text="閉じる", command=win.destroy,
        bg="#3a3a3a", fg="#ffffff", relief="flat", padx=12, pady=4,
    ).pack(side="right", padx=12)

    load_tickets()

