import queue #スレッド間で値を渡す
import sys #終了処理、実行環境
import tkinter as tk #入力ウィンドウの表示

from db import initialize, save_entry
from hotkey import start_hotkey, stop_hotkeys
from tray import start_tray
from ui import show_input_form


def main():
    initialize()
    root = tk.Tk()
    root.withdraw()  # メインウィンドウは非表示

    event_queue = queue.Queue() #event_queueにQueue()の機能を持たせる

    # ホットキーが押されたらキューに "show" を積む
    def on_hotkey():
        print("on_hotkey called")
        event_queue.put("show")

    # トレイの「終了」が押されたらキューに "quit" を積む
    def on_quit(icon):
        icon.stop()
        event_queue.put("quit")

    # 入力確定時の処理
    def on_submit(text):
        save_entry(text)

    def on_show():
        event_queue.put("show")

    start_hotkey(on_hotkey)
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
