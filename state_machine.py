"""
Ties the vision layer and macro layer together into your actual workflow:

    shop (conditional buy loop) -> running (macro) -> reward (tap through) -> shop

Most states are simple "find this template, tap it, move on" and are
declared in STATE_CONFIG. The shop state is special: it needs to keep
tapping Multi-Buy until the Double Coins banner shows, so it has its own
handler (_handle_shop) instead of a single fixed target.
"""
import time

from config import UNKNOWN_SCREEN_TIMEOUT
from macro import MacroPlayer

# Safety cap: max Multi-Buy taps per shop visit before giving up on rolling
# Double Coins and just playing anyway. Prevents draining your whole coin
# balance if the roll doesn't land for a long stretch.
MAX_BUY_ATTEMPTS = 15

# How long (seconds) to wait after tapping Multi-Buy before checking again —
# the "Please wait a moment" / reveal animation needs time to finish.
BUY_REVEAL_WAIT = 2.0


class BotStateMachine:

    STATE_CONFIG = {
        "running":      {"action": "macro",        "target": "stage1_run",   "next": "reward"},
        "reward":       {"action": "tap",           "target": "reward_ok",   "next": "reward_claim"},
        "reward_claim": {"action": "tap_optional",  "target": "claim_button", "next": "shop"},
    }

    def __init__(self, matcher, controller, capture, start_state: str = "shop"):
        self.matcher = matcher
        self.controller = controller
        self.capture = capture
        self.macro_player = MacroPlayer(controller)
        self.state = start_state
        self._unknown_since = None
        self._buy_attempts = 0

    def step(self):
        """Run one cycle: check the screen, act, and advance state."""
        screen_img, bounds = self.capture.capture()
        if screen_img is None:
            print("iPhone Mirroring window not found — waiting...")
            return

        if self.state == "shop":
            self._handle_shop(screen_img, bounds)
            return

        cfg = self.STATE_CONFIG[self.state]

        if cfg["action"] == "macro":
            print(f"[{self.state}] Playing macro '{cfg['target']}'")
            self.macro_player.play(cfg["target"])
            self.state = cfg["next"]
            self._unknown_since = None
            return

        match = self.matcher.find(screen_img, cfg["target"])

        if cfg["action"] == "tap_optional":
            # Claim popups don't always appear — if not found, just move on.
            if match:
                self._tap_match(match, bounds, cfg["target"])
            else:
                print(f"[{self.state}] No '{cfg['target']}' popup — skipping")
            self.state = cfg["next"]
            self._unknown_since = None
            return

        if match:
            self._tap_match(match, bounds, cfg["target"])
            self.state = cfg["next"]
            self._unknown_since = None
        else:
            self._track_unknown(cfg["target"])

    def _handle_shop(self, screen_img, bounds):
        """Shop logic: keep tapping Multi-Buy until the Double Coins banner
        shows (or we hit the attempt cap), then tap Play."""
        banner = self.matcher.find(screen_img, "double_coins_banner")

        if banner:
            play = self.matcher.find(screen_img, "play_button")
            if play:
                print("[shop] Double Coins active -> tap Play")
                self._tap_match(play, bounds, "play_button")
                self.state = "running"
                self._buy_attempts = 0
                self._unknown_since = None
            else:
                self._track_unknown("play_button (with Double Coins active)")
            return

        if self._buy_attempts >= MAX_BUY_ATTEMPTS:
            print(f"[shop] Hit {MAX_BUY_ATTEMPTS} buy attempts without Double Coins — playing anyway")
            play = self.matcher.find(screen_img, "play_button")
            if play:
                self._tap_match(play, bounds, "play_button")
                self.state = "running"
            self._buy_attempts = 0
            self._unknown_since = None
            return

        multi = self.matcher.find(screen_img, "multi_button")
        if multi:
            self._buy_attempts += 1
            print(f"[shop] No Double Coins yet — tapping Multi-Buy (attempt {self._buy_attempts})")
            self._tap_match(multi, bounds, "multi_button")
            time.sleep(BUY_REVEAL_WAIT)
            self._unknown_since = None
        else:
            self._track_unknown("multi_button")

    def _tap_match(self, match, bounds, label):
        rel_x, rel_y, conf = match
        abs_x, abs_y = bounds[0] + rel_x, bounds[1] + rel_y
        print(f"  found '{label}' (confidence {conf:.2f}) -> tap ({abs_x}, {abs_y})")
        self.controller.tap(abs_x, abs_y)

    def _track_unknown(self, label):
        if self._unknown_since is None:
            self._unknown_since = time.time()
        elif time.time() - self._unknown_since > UNKNOWN_SCREEN_TIMEOUT:
            raise RuntimeError(
                f"Stuck in state '{self.state}' for over {UNKNOWN_SCREEN_TIMEOUT}s "
                f"with no match for '{label}'. Stopping so you can check what's "
                f"on screen (popup, error, login prompt, etc.)."
            )
