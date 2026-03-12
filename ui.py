import ctypes
import tkinter as tk


def show_input_form(root, on_submit=None):
    """フローティング入力フォームを表示する。"""
    print("show_input_form called")
    # 既に開いていれば何もしない
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel):
            print("existing toplevel found")
            widget.deiconify()
            widget.lift()
            widget.attributes("-topmost", True)
            widget.update()
            ctypes.windll.user32.SetForegroundWindow(widget.winfo_id())

            for child in widget.winfo_children():
                if isinstance(child, tk.Entry):
                    child.focus_set()
                    child.icursor(tk.END)
                    break
            return

    print("creating new form")
    form = tk.Toplevel(root)
    form.overrideredirect(False)   # タイトルバー
    form.attributes("-topmost", True)
    form.attributes("-alpha", 0.95)

    width, height = 520, 64
    sw = form.winfo_screenwidth()
    sh = form.winfo_screenheight()
    x = (sw - width) // 2
    y = (sh - height) // 2
    form.geometry(f"{width}x{height}+{x}+{y}")
    form.configure(bg="#1e1e1e")

    entry = tk.Entry(
        form,
        font=("Segoe UI", 20),
        bg="#1e1e1e",
        fg="#ffffff",
        insertbackground="#ffffff",
        relief="flat",
        bd=12,
    )
    entry.pack(fill="both", expand=True)
    form.update()
    ctypes.windll.user32.SetForegroundWindow(form.winfo_id())
    entry.focus_set()
    entry.icursor(tk.END)

    def submit(event=None):
        print("submit called")
        text = entry.get().strip()
        print("before destroy")
        form.destroy()
        print("after destroy")
        if text and on_submit:
            on_submit(text)

    def close(event=None):
        print("close called")
        form.destroy()

    entry.bind("<Control-Return>", submit)
    entry.bind("<Escape>", close)
    # フォームの外クリックで閉じる 一旦不要
    #form.bind("<FocusOut>", lambda e: root.after(50, _close_if_lost, form))

"""
def _close_if_lost(form):
    #フォーカスがフォーム外に移っていたら閉じる。
    try:
        focused = form.focus_get()
        if focused is None or str(focused) == str(form.winfo_toplevel()):
            pass
        if str(focused).startswith(str(form)):
            return
        form.destroy()
    except Exception:
        try:
            form.destroy()
        except Exception:
            pass
"""