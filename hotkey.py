"""
Global hotkey listener — lets you stop the bot instantly from anywhere,
even while the game/iPhone Mirroring window has focus, without needing to
switch to Finder or Terminal.

Runs in its own background thread via pynput's GlobalHotKeys.
"""
from pynput import keyboard

from config import STOP_HOTKEY


def start_hotkey_listener(on_stop):
    """Start listening for STOP_HOTKEY in the background. Calls on_stop()
    (no args) when triggered. Returns the listener object — call .stop()
    on it during shutdown."""
    listener = keyboard.GlobalHotKeys({STOP_HOTKEY: on_stop})
    listener.start()
    print(f"Hotkey listener active — press {STOP_HOTKEY} anytime to stop the bot.")
    return listener
