"""
Minimal status window — shows what the bot is currently doing and gives
you a Stop button, so you're not just staring at scrolling Terminal text.

Uses tkinter (built into Python, no extra install needed). Must run on
the main thread on macOS, so main.py runs the bot loop in a background
thread and this window in the main thread instead.
"""
import queue
import tkinter as tk
from tkinter import font as tkfont

from config import STOP_HOTKEY


class StatusWindow:
    def __init__(self, on_stop):
        self.on_stop = on_stop
        self._msg_queue = queue.Queue()

        self.root = tk.Tk()
        self.root.title("CookieRun Bot")
        self.root.geometry("340x160")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        bold = tkfont.Font(size=13, weight="bold")
        mono = tkfont.Font(family="Menlo", size=11)

        tk.Label(self.root, text="CookieRun Bot", font=bold).pack(pady=(10, 2))

        self.state_label = tk.Label(self.root, text="State: starting...", font=mono)
        self.state_label.pack(pady=2)

        self.action_label = tk.Label(
            self.root, text="Last action: —", font=mono, wraplength=310, justify="left"
        )
        self.action_label.pack(pady=2)

        tk.Label(
            self.root, text=f"Hotkey to stop: {STOP_HOTKEY}", fg="gray"
        ).pack(pady=(6, 0))

        stop_btn = tk.Button(
            self.root, text="Stop", command=self._on_stop_clicked,
            bg="#d9534f", fg="white", font=bold, width=12
        )
        stop_btn.pack(pady=10)

        # Poll for updates pushed from the bot thread every 200ms.
        self.root.after(200, self._poll_queue)

    def update_status(self, state: str = None, action: str = None):
        """Thread-safe: call this from the bot's background thread."""
        self._msg_queue.put((state, action))

    def _poll_queue(self):
        try:
            while True:
                state, action = self._msg_queue.get_nowait()
                if state is not None:
                    self.state_label.config(text=f"State: {state}")
                if action is not None:
                    self.action_label.config(text=f"Last action: {action}")
        except queue.Empty:
            pass
        self.root.after(200, self._poll_queue)

    def _on_stop_clicked(self):
        self.state_label.config(text="State: stopping...")
        self.on_stop()

    def _on_close(self):
        self.on_stop()
        self.root.destroy()

    def run(self):
        """Blocks — call this from the main thread."""
        self.root.mainloop()

    def close(self):
        try:
            self.root.quit()
        except Exception:
            pass
