"""Jarvis Orb — CLI entry point.

Usage:
  jarvis-orb           Start Brain + open Orb
  jarvis-orb --brain   Start Brain only (WebSocket server)
  jarvis-orb --orb     Open Orb only
  jarvis-orb --demo    Start demo mode (fake events)
  jarvis-orb --doctor  Check installation health
"""

import argparse
import asyncio
import os
import platform
import shutil
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

    module = "jarvis_brain.demo_server" if demo else "jarvis_brain.mcp_server"
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


def run_doctor():
    """Check installation health and report issues."""
    print()
    print("  \033[36m\033[1mJarvis Orb — Doctor\033[0m")
    print()

    ok_count = 0
    fail_count = 0

    def check(label, passed, detail=""):
        nonlocal ok_count, fail_count
        if passed:
            ok_count += 1
            print(f"  \033[32m✓\033[0m {label}" + (f"  \033[2m({detail})\033[0m" if detail else ""))
        else:
            fail_count += 1
            print(f"  \033[31m✗\033[0m {label}" + (f"  \033[2m({detail})\033[0m" if detail else ""))

    # Python version
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    check("Python 3.11+", sys.version_info >= (3, 11), py_ver)

    # Dependencies
    for pkg in ["aiosqlite", "websockets", "mcp"]:
        try:
            __import__(pkg)
            check(f"Package: {pkg}", True)
        except ImportError:
            check(f"Package: {pkg}", False, "not installed")

    # FastMCP import
    try:
        from mcp.server.fastmcp import FastMCP
        check("FastMCP import", True)
    except ImportError:
        check("FastMCP import", False, "mcp package may be outdated")

    # Brain directory
    brain_dir = os.path.expanduser("~/.jarvis-orb")
    check("Brain directory", os.path.isdir(brain_dir), brain_dir)

    # brain.db
    db_path = os.path.join(brain_dir, "brain.db")
    check("brain.db", os.path.isfile(db_path), db_path if os.path.isfile(db_path) else "not created yet — will be created on first use")

    # Directory permissions (unix only)
    if platform.system() != "Windows" and os.path.isdir(brain_dir):
        mode = oct(os.stat(brain_dir).st_mode)[-3:]
        check("Directory permissions", mode == "700", f"mode={mode}")

    # Claude Code MCP
    claude_bin = shutil.which("claude")
    if claude_bin:
        try:
            result = subprocess.run(["claude", "mcp", "list"], capture_output=True, text=True, timeout=10)
            registered = "jarvis-brain" in result.stdout
            check("Claude Code MCP", registered, "jarvis-brain registered" if registered else "not registered")
        except Exception:
            check("Claude Code MCP", False, "could not check")
    else:
        check("Claude Code CLI", False, "not installed")

    # Orb app
    orb_path = find_orb_app()
    check("Orb app", orb_path is not None, orb_path or "not found")

    # Summary
    print()
    if fail_count == 0:
        print(f"  \033[32mAll {ok_count} checks passed.\033[0m")
    else:
        print(f"  \033[32m{ok_count} passed\033[0m, \033[31m{fail_count} failed\033[0m")
        print(f"  \033[2mRe-run installer: curl -fsSL https://raw.githubusercontent.com/whynowlab/jarvis-orb/main/install.sh | bash\033[0m")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Jarvis Orb — AI Brain + Realtime Visualizer"
    )
    parser.add_argument("--brain", action="store_true", help="Start Brain only")
    parser.add_argument("--orb", action="store_true", help="Open Orb only")
    parser.add_argument("--demo", action="store_true", help="Demo mode (fake events)")
    parser.add_argument("--doctor", action="store_true", help="Check installation health")
    args = parser.parse_args()

    if args.doctor:
        run_doctor()
        return

    print()
    print("  \033[2m          ·  ˚  ·\033[0m")
    print("  \033[2m      · \033[36m⣠⣤⣤⣤⣄\033[2m ·\033[0m")
    print("  \033[2m    ˚ \033[36m⣰⣿⣿⣿⣿⣿⣆\033[2m ˚\033[0m")
    print("  \033[2m      · \033[36m⠻⣿⣿⣿⠟\033[2m ·\033[0m")
    print("  \033[2m          ·  ˚  ·\033[0m")
    print()
    print("  \033[36m\033[1m  J A R V I S  O R B\033[0m")
    print()

    # Determine what to run
    run_brain = args.brain or args.demo or (not args.orb)
    run_orb = args.orb or (not args.brain and not args.demo)

    brain_proc = None
    if run_brain:
        mode = "demo" if args.demo else "brain"
        print(f"  \033[32m✓\033[0m Brain starting ({mode})...")
        brain_proc = start_brain(demo=args.demo)
        time.sleep(1)
        if brain_proc.poll() is None:
            print(f"  \033[32m✓\033[0m Brain running (PID {brain_proc.pid})")
        else:
            print(f"  \033[31m✗\033[0m Brain failed to start")
            return

    if run_orb:
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
        if brain_proc and brain_proc.poll() is None:
            brain_proc.terminate()
            brain_proc.wait(timeout=5)
        print("\n  Stopped.")


if __name__ == "__main__":
    main()
