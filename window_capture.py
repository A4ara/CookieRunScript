"""
Finds the iPhone Mirroring window on screen and grabs screenshots of just
that region, even when it isn't the frontmost window.
"""
import subprocess

import cv2
import Quartz

from config import WINDOW_NAME


class WindowCapture:
    def __init__(self, window_name: str = WINDOW_NAME):
        self.window_name = window_name

    def get_bounds(self):
        """Return (x, y, width, height) of the window, or None if not found."""
        window_list = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID
        )
        for window in window_list:
            owner = window.get("kCGWindowOwnerName", "")
            name = window.get("kCGWindowName", "")
            if self.window_name in (owner, name):
                b = window["kCGWindowBounds"]
                return int(b["X"]), int(b["Y"]), int(b["Width"]), int(b["Height"])
        return None

    def capture(self):
        """Return (image, bounds). image is a cv2/numpy array, or (None, None)
        if the window can't be found."""
        bounds = self.get_bounds()
        if bounds is None:
            return None, None

        x, y, w, h = bounds
        tmp_path = "/tmp/iphone_mirror_capture.png"
        subprocess.run(
            ["screencapture", "-x", "-R", f"{x},{y},{w},{h}", tmp_path],
            check=False,
        )
        img = cv2.imread(tmp_path)
        return img, bounds
