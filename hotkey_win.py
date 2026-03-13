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

_listener_thread_id = None


def _parse_hotkey(hotkey_str):
    """'ctrl+numpad0' → (mods, vk)"""
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
            vk = 0x60 + int(part[6:])
        elif len(part) == 1:
            vk = ord(part.upper())
        elif part.startswith("f") and part[1:].isdigit():
            vk = 0x6F + int(part[1:])
    return mods, vk


def _hotkey_listener(hotkeys: dict):
    """
    hotkeys: {hotkey_id: (mods, vk, callback)}
    全ホットキーを1スレッドで監視し、IDでコールバックを振り分ける
    """
    global _listener_thread_id
    user32 = ctypes.windll.user32
    _listener_thread_id = ctypes.windll.kernel32.GetCurrentThreadId()

    registered = []
    for hotkey_id, (mods, vk, _) in hotkeys.items():
        if user32.RegisterHotKey(None, hotkey_id, mods, vk):
            registered.append(hotkey_id)
            print(f"[hotkey] 登録完了: id={hotkey_id}")
        else:
            print(f"[hotkey] 登録失敗: id={hotkey_id}")

    msg = ctypes.wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
        if msg.message == WM_HOTKEY and msg.wParam in hotkeys:
            _, _, callback = hotkeys[msg.wParam]
            callback()

    for hotkey_id in registered:
        user32.UnregisterHotKey(None, hotkey_id)


def start_hotkey(callbacks: dict, config_path="config.json"):
    """
    callbacks: {"memo": fn, "viewer": fn, ...}
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    hotkey_config = config.get("hotkeys", {})

    # {hotkey_id: (mods, vk, callback)}
    hotkeys = {}
    for hotkey_id, (name, hotkey_str) in enumerate(hotkey_config.items(), start=1):
        if name in callbacks:
            mods, vk = _parse_hotkey(hotkey_str)
            hotkeys[hotkey_id] = (mods, vk, callbacks[name])

    t = threading.Thread(target=_hotkey_listener, args=(hotkeys,), daemon=True)
    t.start()


def stop_hotkeys():
    if _listener_thread_id:
        ctypes.windll.user32.PostThreadMessageW(_listener_thread_id, WM_QUIT, 0, 0)
