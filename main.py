import queue #スレッド間で値を渡す
import sys #終了処理、実行環境
import tkinter as tk #入力ウィンドウの表示

from db import initialize, save_entry
from task_log.task_form import show_task_form, show_task_detail
from hotkey import start_hotkey, stop_hotkeys
from ticket_viewer import show_ticket
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

    def on_ticket_view():                                                
        event_queue.put("ticket_view")  

    def on_gantt():
        event_queue.put("make_gantt")

    def on_task_detail():
        event_queue.put("task_detail")

    # トレイコールバック
    def on_show():
        event_queue.put("show")

    def on_quit(icon):
        icon.stop()
        event_queue.put("quit")

    start_hotkey({
        "memo": on_memo, 
        "viewer": on_viewer, 
        "ticket": on_ticket, 
        "ticket_view": on_ticket_view,
        "make_gantt":  on_gantt,
        "task_detail":  on_task_detail,
        })
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
                elif event == "ticket_view":
                    show_ticket(root)
                elif event == "make_gantt":
                    show_task_form(root)
                elif event == "task_detail":
                    show_task_detail(root)
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
