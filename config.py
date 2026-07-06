"""
Central configuration for the Cookie Run Classic auto-bot.
Tweak these values as you tune the bot for your setup.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
MACROS_DIR = os.path.join(BASE_DIR, "macros")

# Name of the window to find and capture (must match exactly)
WINDOW_NAME = "iPhone Mirroring"

# How confident a template match must be to count as "found" (0.0 - 1.0)
CONFIDENCE_THRESHOLD = 0.85

# Random range (seconds) between screen checks in the main loop
SCAN_INTERVAL = (1.0, 2.0)

# Pause after a tap before the next screen check
CLICK_COOLDOWN = 0.5

# If the bot sits on an unrecognized screen this long (seconds), it stops
# itself rather than clicking blindly. Raise this if your game legitimately
# has slow loading screens.
UNKNOWN_SCREEN_TIMEOUT = 15

# Random +/- pixel offset added to every tap so repeated taps aren't
# pixel-identical every single time.
JITTER_PIXELS = 3

# Global hotkey to stop the bot instantly from anywhere (works even while
# the game/iPhone Mirroring window has focus). Format uses pynput syntax:
# <ctrl>, <shift>, <cmd>, <alt> as modifiers, plus a regular key.
STOP_HOTKEY = "<cmd>+<shift>+x"
