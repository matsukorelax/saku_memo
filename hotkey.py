import ctypes
import ctypes.wintypes
import json
import threading

MOD_ALT      = 0x0001
MOD_CONTROL  = 0x0002
MOD_SHIFT    = 0x0004
MOD_WIN      = 0x0008
MOD_NOREPEAT = 0x4000
WM_HOTKEY    = 0x0312
WM_QUIT      = 0x0012
HOTKEY_ID    = 1

_listener_thread_id = None


def _parse_hotkey(hotkey_str):
    """'ctrl+shift+k' → (mods, vk)"""
    parts = [p.strip().lower() for p in hotkey_str.split("+")]
    mods = MOD_NOREPEAT
    vk = 0
    for part in parts:
        if part == "ctrl":
            mods |= MOD_CONTROL
        elif part == "shift":
            mods |= MOD_SHIFT
        elif part == "alt":
            mods |= MOD_ALT
        elif part == "win":
            mods |= MOD_WIN
        elif part.startswith("numpad") and part[6:].isdigit():
            vk = 0x60 + int(part[6:])  # numpad0=0x60, numpad1=0x61 ...
        elif len(part) == 1:
            vk = ord(part.upper())
        elif part.startswith("f") and part[1:].isdigit():
            vk = 0x6F + int(part[1:])  # F1=0x70, F2=0x71 ...
    return mods, vk


def _hotkey_listener(mods, vk, callback):
    global _listener_thread_id
    user32 = ctypes.windll.user32
    _listener_thread_id = ctypes.windll.kernel32.GetCurrentThreadId()

    if not user32.RegisterHotKey(None, HOTKEY_ID, mods, vk):
        print("[hotkey] 登録失敗 (他のアプリが同じキーを使用している可能性があります)")
        return

    print(f"[hotkey] 登録完了")
    msg = ctypes.wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
        if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
            callback()

    user32.UnregisterHotKey(None, HOTKEY_ID)


def start_hotkey(callback, config_path="config.json"):
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    hotkey_str = config.get("hotkey", "ctrl+shift+k")
    mods, vk = _parse_hotkey(hotkey_str)

    t = threading.Thread(target=_hotkey_listener, args=(mods, vk, callback), daemon=True)
    t.start()


def stop_hotkeys():
    if _listener_thread_id:
        ctypes.windll.user32.PostThreadMessageW(_listener_thread_id, WM_QUIT, 0, 0)
