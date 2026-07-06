"""
The "hands" layer: sends taps and swipes to the screen via cliclick.
Kept as its own module so you can swap in pyautogui/pynput without
touching anything else.
"""
import random
import subprocess

from config import JITTER_PIXELS


class InputController:
    def tap(self, x: int, y: int, jitter: int = JITTER_PIXELS):
        jx = x + random.randint(-jitter, jitter)
        jy = y + random.randint(-jitter, jitter)
        subprocess.run(["cliclick", f"c:{jx},{jy}"], check=False)

    def swipe(self, x1: int, y1: int, x2: int, y2: int):
        """Simple drag from one point to another."""
        subprocess.run(["cliclick", f"dd:{x1},{y1}"], check=False)
        subprocess.run(["cliclick", f"m:{x2},{y2}"], check=False)
        subprocess.run(["cliclick", f"du:{x2},{y2}"], check=False)
