import json
import threading
from Xlib import X, XK
from Xlib.display import Display
from Xlib.ext import record
from Xlib.protocol import rq

_stop_event = threading.Event()
_listener_thread = None
_display = None


def _parse_hotkey(hotkey_str):
    """'ctrl+shift+k' → (modifiers, keysym)"""
    parts = [p.strip().lower() for p in hotkey_str.split("+")]
    mods = 0
    keysym = None
    for part in parts:
        if part == "ctrl":
            mods |= X.ControlMask
        elif part == "shift":
            mods |= X.ShiftMask
        elif part == "alt":
            mods |= X.Mod1Mask
        elif part == "win":
            mods |= X.Mod4Mask
        elif part.startswith("numpad") and part[6:].isdigit():
            keysym = getattr(XK, f"XK_KP_{part[6:]}", None)
        elif part.startswith("f") and part[1:].isdigit():
            keysym = getattr(XK, f"XK_F{part[1:]}", None)
        elif len(part) == 1:
            keysym = XK.string_to_keysym(part)
    return mods, keysym


def _hotkey_listener(mods, keysym, callback):
    global _display
    _display = Display()
    root = _display.screen().root

    keycode = _display.keysym_to_keycode(keysym)
    if keycode == 0:
        print("[hotkey] 登録失敗 (キーコードが見つかりません)")
        return

    root.grab_key(keycode, mods, True, X.GrabModeAsync, X.GrabModeAsync)
    _display.flush()
    print("[hotkey] 登録完了")

    while not _stop_event.is_set():
        if _display.pending_events():
            event = _display.next_event()
            if event.type == X.KeyPress:
                callback()
        else:
            _stop_event.wait(timeout=0.05)

    root.ungrab_key(keycode, mods)
    _display.flush()
    _display.close()


def start_hotkey(callback, config_path="config.json"):
    global _listener_thread
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    hotkey_str = config.get("hotkey", "ctrl+shift+k")
    mods, keysym = _parse_hotkey(hotkey_str)

    _stop_event.clear()
    _listener_thread = threading.Thread(
        target=_hotkey_listener, args=(mods, keysym, callback), daemon=True
    )
    _listener_thread.start()


def stop_hotkeys():
    _stop_event.set()
