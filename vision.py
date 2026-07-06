"""
The "brain" layer: loads button template images and finds them in a
captured screenshot. This is what lets the bot know what screen it's on.
"""
import os

import cv2

from config import TEMPLATES_DIR, CONFIDENCE_THRESHOLD


class TemplateMatcher:
    def __init__(self, templates_dir: str = TEMPLATES_DIR):
        self.templates_dir = templates_dir
        self.templates = self._load_templates()

    def _load_templates(self):
        templates = {}
        if not os.path.isdir(self.templates_dir):
            return templates
        for fname in sorted(os.listdir(self.templates_dir)):
            if fname.lower().endswith(".png"):
                name = os.path.splitext(fname)[0]
                img = cv2.imread(os.path.join(self.templates_dir, fname))
                if img is not None:
                    templates[name] = img
        return templates

    def reload(self):
        """Call this if you add/remove template files while the bot is running."""
        self.templates = self._load_templates()

    def find(self, screen_img, name: str, threshold: float = CONFIDENCE_THRESHOLD):
        """Look for one named template. Returns (x, y, confidence) relative
        to the screenshot, or None."""
        template = self.templates.get(name)
        if template is None or screen_img is None:
            return None
        if template.shape[0] > screen_img.shape[0] or template.shape[1] > screen_img.shape[1]:
            return None

        result = cv2.matchTemplate(screen_img, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val >= threshold:
            th, tw = template.shape[:2]
            return max_loc[0] + tw // 2, max_loc[1] + th // 2, max_val
        return None

    def find_best(self, screen_img, threshold: float = CONFIDENCE_THRESHOLD):
        """Scan every loaded template, return the single best match as
        (name, x, y, confidence), or None if nothing clears the threshold."""
        best = None
        for name in self.templates:
            match = self.find(screen_img, name, threshold)
            if match:
                x, y, conf = match
                if best is None or conf > best[3]:
                    best = (name, x, y, conf)
        return best
