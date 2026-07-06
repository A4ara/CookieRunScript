"""
Entry point. Run this to start the bot:

    python3 main.py

Two ways to stop it:
  - Press the hotkey (see STOP_HOTKEY in config.py, default Cmd+Shift+X)
    from anywhere, even with the game in focus.
  - Click "Stop" in the small status window that opens.

The bot also stops itself if it gets stuck on an unrecognized screen for
too long (see UNKNOWN_SCREEN_TIMEOUT in config.py).
"""
import random
import threading
import time

from config import SCAN_INTERVAL
from window_capture import WindowCapture
from vision import TemplateMatcher
from input_controller import InputController
from state_machine import BotStateMachine
from status_window import StatusWindow
from hotkey import start_hotkey_listener

stop_event = threading.Event()


def bot_loop(status: StatusWindow):
    capture = WindowCapture()
    matcher = TemplateMatcher()
    controller = InputController()
    bot = BotStateMachine(matcher, controller, capture, stop_event=stop_event)

    if not matcher.templates:
        status.update_status(state="error", action="No templates found in templates/")
        return

    required = {"play_button", "multi_button", "double_coins_banner", "reward_ok"}
    missing = required - set(matcher.templates.keys())
    if missing:
        print(f"Warning: missing templates for {sorted(missing)} — those states will stall.")

    status.update_status(state=bot.state, action="Bot started")

    while not stop_event.is_set():
        try:
            prev_state = bot.state
            bot.step()
            if bot.state != prev_state:
                status.update_status(state=bot.state, action=f"{prev_state} -> {bot.state}")
        except RuntimeError as e:
            status.update_status(state="stopped", action=str(e))
            print(f"\nBot stopped itself: {e}")
            break
        time.sleep(random.uniform(*SCAN_INTERVAL))

    status.update_status(state="stopped", action="Bot loop ended")


def main():
    status = StatusWindow(on_stop=stop_event.set)

    hotkey_listener = start_hotkey_listener(on_stop=lambda: (stop_event.set(), status.close()))

    worker = threading.Thread(target=bot_loop, args=(status,), daemon=True)
    worker.start()

    try:
        status.run()  # blocks on main thread until window closes or Stop is clicked
    finally:
        stop_event.set()
        hotkey_listener.stop()
        print("\nStopped.")


if __name__ == "__main__":
    main()
