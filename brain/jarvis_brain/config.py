"""Jarvis Brain Lite — Configuration."""
from pathlib import Path

BRAIN_DIR = Path.home() / ".jarvis-orb"
BRAIN_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = BRAIN_DIR / "brain.db"
WS_PORT = 9321
