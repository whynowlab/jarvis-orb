"""Jarvis Brain Lite — Configuration."""
from pathlib import Path

BRAIN_DIR = Path.home() / ".jarvis-orb"
DB_PATH = BRAIN_DIR / "brain.db"
WS_PORT = 9321


def ensure_dirs():
    """Create brain directory on demand (not on import)."""
    BRAIN_DIR.mkdir(parents=True, exist_ok=True)
