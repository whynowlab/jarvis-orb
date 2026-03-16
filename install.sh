#!/bin/bash
# Jarvis Orb — One-command installer
# Usage: curl -fsSL https://raw.githubusercontent.com/whynowlab/jarvis-orb/main/install.sh | bash

set -e

echo ""
echo "  ╭─────────────────────────────────────╮"
echo "  │         Jarvis Orb Installer         │"
echo "  │   AI Brain Visualizer + Memory MCP   │"
echo "  ╰─────────────────────────────────────╯"
echo ""

REPO="whynowlab/jarvis-orb"
BRAIN_DIR="$HOME/.jarvis-orb"
BRAIN_BIN="$BRAIN_DIR/bin"

# Detect OS
OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
  Darwin) PLATFORM="macos" ;;
  Linux)  PLATFORM="linux" ;;
  MINGW*|MSYS*|CYGWIN*) PLATFORM="windows" ;;
  *) echo "Unsupported OS: $OS"; exit 1 ;;
esac

echo "[1/5] Detecting environment..."
echo "  OS: $OS ($ARCH)"
echo "  Platform: $PLATFORM"
echo "  Brain dir: $BRAIN_DIR"

# Step 1: Create directories
echo ""
echo "[2/5] Setting up Jarvis Brain..."
mkdir -p "$BRAIN_DIR" "$BRAIN_BIN"

# Step 2: Install Brain Lite (Python MCP server)
if command -v uv &>/dev/null; then
  echo "  Using uv to install brain..."
  uv pip install --target "$BRAIN_DIR/lib" aiosqlite websockets 2>/dev/null || true
elif command -v pip3 &>/dev/null; then
  echo "  Using pip3 to install brain..."
  pip3 install --target "$BRAIN_DIR/lib" aiosqlite websockets 2>/dev/null || true
else
  echo "  Warning: Python package manager not found."
  echo "  Please install 'uv' or 'pip3' for full Brain Lite functionality."
fi

# Copy Brain Lite source
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
if [ -d "$SCRIPT_DIR/brain/jarvis_brain" ]; then
  cp -r "$SCRIPT_DIR/brain/jarvis_brain" "$BRAIN_DIR/jarvis_brain"
  echo "  Brain Lite installed to $BRAIN_DIR/jarvis_brain"
else
  # Download from GitHub if running via curl
  echo "  Downloading Brain Lite from GitHub..."
  curl -fsSL "https://github.com/$REPO/archive/refs/heads/main.tar.gz" | \
    tar -xz --strip-components=2 -C "$BRAIN_DIR" "jarvis-orb-main/brain/jarvis_brain" 2>/dev/null || true
fi

# Step 3: Create Brain launcher
cat > "$BRAIN_BIN/jarvis-brain" << 'LAUNCHER'
#!/bin/bash
BRAIN_DIR="$HOME/.jarvis-orb"
export PYTHONPATH="$BRAIN_DIR/lib:$BRAIN_DIR"
python3 -m jarvis_brain.mcp_server "$@"
LAUNCHER
chmod +x "$BRAIN_BIN/jarvis-brain"

# Step 4: Configure Claude Code MCP
echo ""
echo "[3/5] Configuring Claude Code MCP..."

CLAUDE_SETTINGS="$HOME/.claude/settings.json"
if [ -f "$CLAUDE_SETTINGS" ]; then
  # Check if already configured
  if grep -q "jarvis-brain" "$CLAUDE_SETTINGS" 2>/dev/null; then
    echo "  Already configured in Claude Code."
  else
    echo "  Adding Jarvis Brain MCP server to Claude Code..."
    echo ""
    echo "  To complete setup, add this to your Claude Code MCP config:"
    echo ""
    echo '  "jarvis-brain": {'
    echo '    "command": "'$BRAIN_BIN'/jarvis-brain"'
    echo '  }'
    echo ""
  fi
else
  echo "  Claude Code settings not found. Skipping MCP config."
  echo "  You can manually add Jarvis Brain as an MCP server later."
fi

# Step 5: Download Orb app
echo ""
echo "[4/5] Installing Jarvis Orb app..."

if [ "$PLATFORM" = "macos" ]; then
  LATEST=$(curl -fsSL "https://api.github.com/repos/$REPO/releases/latest" 2>/dev/null | grep "browser_download_url.*dmg" | head -1 | cut -d'"' -f4)
  if [ -n "$LATEST" ]; then
    echo "  Downloading Orb from $LATEST..."
    curl -fsSL -o "/tmp/JarvisOrb.dmg" "$LATEST"
    echo "  Mounting DMG..."
    hdiutil attach "/tmp/JarvisOrb.dmg" -quiet
    cp -r "/Volumes/Jarvis Orb/Jarvis Orb.app" "/Applications/" 2>/dev/null || true
    hdiutil detach "/Volumes/Jarvis Orb" -quiet 2>/dev/null || true
    rm -f "/tmp/JarvisOrb.dmg"
    echo "  Jarvis Orb.app installed to /Applications/"
  else
    echo "  No release found. Build from source:"
    echo "  cd orb && pnpm install && cargo tauri build"
  fi
elif [ "$PLATFORM" = "windows" ]; then
  LATEST=$(curl -fsSL "https://api.github.com/repos/$REPO/releases/latest" 2>/dev/null | grep "browser_download_url.*msi" | head -1 | cut -d'"' -f4)
  if [ -n "$LATEST" ]; then
    echo "  Download Orb installer: $LATEST"
  else
    echo "  No Windows release found yet. Build from source or wait for CI."
  fi
fi

# Done
echo ""
echo "[5/5] Done!"
echo ""
echo "  ╭──────────────────────────────────────────╮"
echo "  │  Jarvis Orb installed successfully!       │"
echo "  │                                           │"
echo "  │  Brain: ~/.jarvis-orb/                    │"
echo "  │  DB:    ~/.jarvis-orb/brain.db            │"
echo "  │                                           │"
echo "  │  Start: jarvis-brain (MCP server)         │"
echo "  │  Orb:   open Jarvis Orb.app               │"
echo "  │                                           │"
echo "  │  Your AI will start remembering.          │"
echo "  ╰──────────────────────────────────────────╯"
echo ""
