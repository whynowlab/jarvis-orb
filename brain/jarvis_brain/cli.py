"""Jarvis Orb — CLI entry point.

Usage:
  jarvis-orb          Start Brain + open Orb
  jarvis-orb --brain  Start Brain only (WebSocket server)
  jarvis-orb --orb    Open Orb only
  jarvis-orb --demo   Start demo mode (fake events)
"""

import argparse
import asyncio
import os
import platform
import subprocess
import sys
import time


def find_orb_app():
    """Find the Orb app on disk."""
    system = platform.system()
    if system == "Darwin":
        paths = [
            "/Applications/Jarvis Orb.app",
            os.path.expanduser("~/Applications/Jarvis Orb.app"),
        ]
        for p in paths:
            if os.path.exists(p):
                return p
    elif system == "Windows":
        # Common install locations
        appdata = os.environ.get("LOCALAPPDATA", "")
        paths = [
            os.path.join(appdata, "Jarvis Orb", "Jarvis Orb.exe"),
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Jarvis Orb", "Jarvis Orb.exe"),
        ]
        for p in paths:
            if os.path.exists(p):
                return p
    return None


def start_brain(demo=False):
    """Start Brain Lite WebSocket server in background."""
    brain_dir = os.path.expanduser("~/.jarvis-orb")
    lib_dir = os.path.join(brain_dir, "lib")
    sep = ";" if platform.system() == "Windows" else ":"
    pythonpath = f"{lib_dir}{sep}{brain_dir}"

    module = "jarvis_brain.demo_server" if demo else "jarvis_brain.demo_server"
    python = "python" if platform.system() == "Windows" else "python3"

    env = os.environ.copy()
    env["PYTHONPATH"] = pythonpath

    proc = subprocess.Popen(
        [python, "-m", module],
        cwd=brain_dir,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc


def open_orb():
    """Open the Orb desktop app."""
    app_path = find_orb_app()
    if not app_path:
        print("  Orb app not found. Install it first.")
        return None

    system = platform.system()
    if system == "Darwin":
        subprocess.Popen(["open", app_path])
    elif system == "Windows":
        subprocess.Popen([app_path])
    return app_path


def main():
    parser = argparse.ArgumentParser(
        description="Jarvis Orb — AI Brain + Realtime Visualizer"
    )
    parser.add_argument("--brain", action="store_true", help="Start Brain only")
    parser.add_argument("--orb", action="store_true", help="Open Orb only")
    parser.add_argument("--demo", action="store_true", help="Demo mode (fake events)")
    args = parser.parse_args()

    print()
    print("  \033[36m\033[1mJARVIS ORB\033[0m")
    print()

    if args.brain or (not args.orb):
        mode = "demo" if args.demo else "brain"
        print(f"  \033[32m✓\033[0m Brain starting...")
        brain_proc = start_brain(demo=args.demo)
        time.sleep(1)
        if brain_proc.poll() is None:
            print(f"  \033[32m✓\033[0m Brain running (PID {brain_proc.pid})")
        else:
            print(f"  \033[31m✗\033[0m Brain failed to start")
            return

    if args.orb or (not args.brain):
        print(f"  \033[32m✓\033[0m Opening Orb...")
        path = open_orb()
        if path:
            print(f"  \033[32m✓\033[0m Orb launched")

    print()
    print("  \033[36mYour AI is thinking.\033[0m")
    print("  \033[2mPress Ctrl+C to stop.\033[0m")
    print()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  Stopped.")


if __name__ == "__main__":
    main()
