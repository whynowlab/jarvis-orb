#!/bin/bash
# Jarvis Orb — Installer
# curl -fsSL https://raw.githubusercontent.com/whynowlab/jarvis-orb/main/install.sh | bash

set -e

# ── Colors ──
R='\033[0m'
B='\033[1m'
DIM='\033[2m'
CYAN='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
WHITE='\033[97m'
BG='\033[48;5;236m'

REPO="whynowlab/jarvis-orb"
VERSION="0.1.0"
BRAIN_DIR="$HOME/.jarvis-orb"
BRAIN_BIN="$BRAIN_DIR/bin"

# ── Header ──
echo ""
echo ""
echo -e "  ${CYAN}${B}JARVIS ORB${R}"
echo -e "  ${DIM}AI Brain + Realtime Visualizer${R}"
echo -e "  ${DIM}v${VERSION}${R}"
echo ""

# ── Detect ──
OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
  Darwin) PLATFORM="macos" ;;
  Linux)  PLATFORM="linux" ;;
  MINGW*|MSYS*|CYGWIN*) PLATFORM="windows" ;;
  *) echo -e "  ${RED}Unsupported: $OS${R}"; exit 1 ;;
esac

step() {
  echo ""
  echo -e "  ${CYAN}→${R} ${B}$1${R}"
}

info() {
  echo -e "    ${DIM}$1${R}"
}

ok() {
  echo -e "    ${GREEN}✓${R} $1"
}

warn() {
  echo -e "    ${YELLOW}!${R} $1"
}

fail() {
  echo -e "    ${RED}✗${R} $1"
}

# ── Step 1: Environment ──
step "Checking environment"
info "$OS $ARCH"

if command -v uv &>/dev/null; then
  ok "uv found"
  PIP_CMD="uv pip install"
elif command -v pip3 &>/dev/null; then
  ok "pip3 found"
  PIP_CMD="pip3 install"
else
  warn "No Python package manager — Brain Lite requires uv or pip3"
  PIP_CMD=""
fi

if command -v node &>/dev/null; then
  ok "Node $(node -v)"
fi

# ── Step 2: Brain Lite ──
step "Installing Brain Lite"

mkdir -p "$BRAIN_DIR" "$BRAIN_BIN"

if [ -n "$PIP_CMD" ]; then
  $PIP_CMD --target "$BRAIN_DIR/lib" aiosqlite websockets >/dev/null 2>&1 && \
    ok "Dependencies installed" || warn "Dependency install failed"
fi

# Download Brain source
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
if [ -d "$SCRIPT_DIR/brain/jarvis_brain" ]; then
  cp -r "$SCRIPT_DIR/brain/jarvis_brain" "$BRAIN_DIR/jarvis_brain"
  ok "Brain Lite → ~/.jarvis-orb/"
else
  curl -fsSL "https://github.com/$REPO/archive/refs/heads/main.tar.gz" 2>/dev/null | \
    tar -xz --strip-components=2 -C "$BRAIN_DIR" "jarvis-orb-main/brain/jarvis_brain" 2>/dev/null && \
    ok "Brain Lite downloaded" || warn "Download failed — install from source"
fi

# Launcher script
cat > "$BRAIN_BIN/jarvis-brain" << 'EOF'
#!/bin/bash
export PYTHONPATH="$HOME/.jarvis-orb/lib:$HOME/.jarvis-orb"
exec python3 -m jarvis_brain.mcp_server "$@"
EOF
chmod +x "$BRAIN_BIN/jarvis-brain"
ok "Brain launcher → ~/.jarvis-orb/bin/jarvis-brain"

# ── Step 3: Claude Code MCP ──
step "Configuring Claude Code"

CLAUDE_DIR="$HOME/.claude"
CLAUDE_SETTINGS="$CLAUDE_DIR/settings.json"

if [ -d "$CLAUDE_DIR" ]; then
  if grep -q "jarvis-brain" "$CLAUDE_SETTINGS" 2>/dev/null; then
    ok "Already configured"
  else
    info "Add to your Claude Code MCP config:"
    echo ""
    echo -e "    ${WHITE}\"jarvis-brain\": {${R}"
    echo -e "    ${WHITE}  \"command\": \"$BRAIN_BIN/jarvis-brain\"${R}"
    echo -e "    ${WHITE}}${R}"
    echo ""
  fi
else
  info "Claude Code not found — configure MCP manually after install"
fi

# ── Step 4: Orb App ──
step "Installing Orb"

if [ "$PLATFORM" = "macos" ]; then
  LATEST=$(curl -fsSL "https://api.github.com/repos/$REPO/releases/latest" 2>/dev/null | \
    grep "browser_download_url.*dmg" | head -1 | cut -d'"' -f4)
  if [ -n "$LATEST" ]; then
    info "Downloading..."
    curl -fsSL -o "/tmp/JarvisOrb.dmg" "$LATEST"
    hdiutil attach "/tmp/JarvisOrb.dmg" -quiet
    cp -r "/Volumes/Jarvis Orb/Jarvis Orb.app" "/Applications/" 2>/dev/null || true
    hdiutil detach "/Volumes/Jarvis Orb" -quiet 2>/dev/null || true
    rm -f "/tmp/JarvisOrb.dmg"
    ok "Jarvis Orb.app → /Applications/"
  else
    warn "No release found — build: cd orb && pnpm install && cargo tauri build"
  fi
elif [ "$PLATFORM" = "windows" ]; then
  LATEST=$(curl -fsSL "https://api.github.com/repos/$REPO/releases/latest" 2>/dev/null | \
    grep "browser_download_url.*msi" | head -1 | cut -d'"' -f4)
  if [ -n "$LATEST" ]; then
    info "Download: $LATEST"
    ok "Run the .msi installer after download"
  else
    warn "No Windows release yet"
  fi
fi

# ── Done ──
echo ""
echo ""
echo -e "  ${GREEN}${B}Installed.${R}"
echo ""
echo -e "  ${DIM}Brain${R}   ~/.jarvis-orb/brain.db"
echo -e "  ${DIM}MCP${R}     jarvis-brain"
echo -e "  ${DIM}Orb${R}     Jarvis Orb.app"
echo ""
echo -e "  ${CYAN}Your AI will start remembering.${R}"
echo ""
