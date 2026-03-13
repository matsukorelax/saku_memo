import queue #スレッド間で値を渡す
import sys #終了処理、実行環境
import tkinter as tk #入力ウィンドウの表示

from db import initialize, save_entry
from hotkey import start_hotkey, stop_hotkeys
from tray import start_tray
from ui import show_input_form
from viewer import show_viewer
from ticket_form import show_ticket_form


def main():
    initialize()
    root = tk.Tk()
    root.withdraw()  # メインウィンドウは非表示

    event_queue = queue.Queue() #event_queueにQueue()の機能を持たせる

    # 入力確定時の処理
    def on_submit(text):
        save_entry(text)

    # ホットキーコールバック
    def on_memo():
        event_queue.put("show")

    def on_viewer():
        event_queue.put("viewer")

    def on_ticket():
        event_queue.put("ticket")

    # トレイコールバック
    def on_show():
        event_queue.put("show")

    def on_quit(icon):
        icon.stop()
        event_queue.put("quit")

    start_hotkey({"memo": on_memo, "viewer": on_viewer, "ticket": on_ticket})
    start_tray(on_show, on_quit)

    def process_events():
        try:
            while True:
                event = event_queue.get_nowait()
                if event == "show":
                    try:
                        show_input_form(root, on_submit=on_submit)
                    except Exception as e:
                        print(f"[error] show_input_form: {e}")
                elif event == "viewer":
                    show_viewer(root)
                elif event == "ticket":
                    show_ticket_form(root)
                elif event == "quit":
                    stop_hotkeys()
                    root.quit()
                    sys.exit(0)
        except queue.Empty:
            pass
        root.after(100, process_events)

    root.after(100, process_events)
    root.mainloop()


if __name__ == "__main__":
    main()
