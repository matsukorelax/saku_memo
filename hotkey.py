import sys

if sys.platform == "win32":
    from hotkey_win import start_hotkey, stop_hotkeys
else:
    from hotkey_linux import start_hotkey, stop_hotkeys
