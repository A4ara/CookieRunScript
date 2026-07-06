"""
Entry point. Run this to start the bot:

    python3 main.py

Stop anytime with Ctrl+C. The bot also stops itself if it gets stuck on an
unrecognized screen (see UNKNOWN_SCREEN_TIMEOUT in config.py).
"""
import random
import time

from config import SCAN_INTERVAL
from window_capture import WindowCapture
from vision import TemplateMatcher
from input_controller import InputController
from state_machine import BotStateMachine


def main():
    capture = WindowCapture()
    matcher = TemplateMatcher()
    controller = InputController()
    bot = BotStateMachine(matcher, controller, capture)

    if not matcher.templates:
        print("No templates loaded from templates/ — add button screenshots first.")
        print("See README.md for instructions.")
        return

    required = {"play_button", "multi_button", "double_coins_banner", "reward_ok"}
    missing = required - set(matcher.templates.keys())
    if missing:
        print(f"Warning: missing templates for {sorted(missing)} — those states will stall.")

    print(f"Loaded templates: {list(matcher.templates.keys())}")
    print("Bot starting. Press Ctrl+C to stop.\n")

    try:
        while True:
            bot.step()
            time.sleep(random.uniform(*SCAN_INTERVAL))
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except RuntimeError as e:
        print(f"\nBot stopped itself: {e}")


if __name__ == "__main__":
    main()
