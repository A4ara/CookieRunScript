"""
Records and replays fixed click sequences — for the "running" segment of a
stage, where the layout is the same every time (jump/slide/skill inputs).

Since your stages are fixed layouts, record each stage ONCE by hand while
playing normally, then replay that exact sequence every future run.

Usage to record a new macro:
    python3 macro.py stage1_run

Then click through the stage in the iPhone Mirroring window as you'd play
it. Press Ctrl+C in the terminal when the stage ends to stop recording.
This saves macros/stage1_run.json.
"""
import json
import os
import sys
import time

from pynput import mouse

from config import MACROS_DIR
from input_controller import InputController


class MacroRecorder:
    def __init__(self):
        self.events = []
        self.start_time = None
        self.listener = None

    def _on_click(self, x, y, button, pressed):
        if not pressed:
            return
        t = time.time() - self.start_time
        self.events.append({"t": round(t, 3), "x": x, "y": y})
        print(f"Recorded click at ({x}, {y})  t={t:.3f}s")

    def record(self):
        print("Recording started — click through the stage now.")
        print("Press Ctrl+C in this terminal when done.\n")
        self.start_time = time.time()
        self.listener = mouse.Listener(on_click=self._on_click)
        self.listener.start()
        try:
            self.listener.join()
        except KeyboardInterrupt:
            self.listener.stop()

    def save(self, name: str):
        os.makedirs(MACROS_DIR, exist_ok=True)
        path = os.path.join(MACROS_DIR, f"{name}.json")
        with open(path, "w") as f:
            json.dump(self.events, f, indent=2)
        print(f"\nSaved {len(self.events)} clicks to {path}")


class MacroPlayer:
    def __init__(self, controller: InputController = None):
        self.controller = controller or InputController()

    def load(self, name: str):
        path = os.path.join(MACROS_DIR, f"{name}.json")
        with open(path) as f:
            return json.load(f)

    def play(self, name: str, speed: float = 1.0, stop_event=None):
        """Replay a saved macro. speed > 1.0 plays faster, < 1.0 slower.
        If stop_event is given and gets set mid-playback, stops early
        instead of finishing the whole recorded sequence."""
        events = self.load(name)
        last_t = 0.0
        for ev in events:
            if stop_event is not None and stop_event.is_set():
                print("Macro playback interrupted by stop signal.")
                return
            wait = (ev["t"] - last_t) / speed
            self._interruptible_sleep(wait, stop_event)
            self.controller.tap(ev["x"], ev["y"])
            last_t = ev["t"]

    @staticmethod
    def _interruptible_sleep(seconds: float, stop_event=None, chunk: float = 0.1):
        """Sleep in small chunks so a stop signal lands within `chunk`
        seconds instead of waiting out one long time.sleep() call."""
        remaining = seconds
        while remaining > 0:
            if stop_event is not None and stop_event.is_set():
                return
            step = min(chunk, remaining)
            time.sleep(step)
            remaining -= step


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 macro.py <macro_name>")
        sys.exit(1)

    recorder = MacroRecorder()
    recorder.record()
    recorder.save(sys.argv[1])
