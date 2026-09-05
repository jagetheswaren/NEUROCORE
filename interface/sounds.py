"""Optional, local-only UI sounds for the terminal interface."""

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class SoundEngine:
    """Play short UI sounds only when explicitly enabled."""

    def __init__(self, enabled=False, volume=0.2, assets_dir=None):
        self.enabled = bool(enabled)
        self.volume = max(0.0, min(float(volume), 1.0))
        self.assets_dir = Path(assets_dir or Path(__file__).parent.parent / "assets" / "sounds")

    def set_enabled(self, enabled):
        self.enabled = bool(enabled)

    def status(self):
        return {"enabled": self.enabled, "volume": self.volume}

    def play(self, name):
        if not self.enabled:
            return False
        path = self.assets_dir / f"{name}.wav"
        if not path.is_file():
            logger.debug("Sound asset unavailable: %s", path)
            return False
        try:
            import winsound
            winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
            return True
        except (ImportError, OSError) as error:
            logger.warning("Unable to play sound %s: %s", name, error)
            return False
