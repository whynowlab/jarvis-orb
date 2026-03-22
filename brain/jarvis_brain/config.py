"""Jarvis Brain Lite — Configuration."""
import os
from pathlib import Path

BRAIN_DIR = Path.home() / ".jarvis-orb"
DB_PATH = BRAIN_DIR / "brain.db"
WS_PORT = 9321


def ensure_dirs():
    """Create brain directory on demand (not on import)."""
    BRAIN_DIR.mkdir(parents=True, exist_ok=True)
    # Restrict permissions to owner only
    try:
        os.chmod(BRAIN_DIR, 0o700)
    except OSError:
        pass
