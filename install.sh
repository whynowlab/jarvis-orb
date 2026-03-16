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
HOLO='\033[38;2;142;228;255m'

REPO="whynowlab/jarvis-orb"
VERSION="0.3.1"
BRAIN_DIR="$HOME/.jarvis-orb"
BRAIN_BIN="$BRAIN_DIR/bin"

# ── Logo ──
show_logo() {
  echo ""
  # Generate logo with oh-my-logo if available, else fallback
  if command -v npx &>/dev/null; then
    npx -y oh-my-logo "JARVIS" --palette-colors "#4A9EBF,#8EE4FF,#6B4FA0" --filled --block-font block -d diagonal --color 2>/dev/null
    echo -e "                                  ${HOLO}◉ ORB${R}"
    echo -e "                                  ${DIM}AI Brain + Visualizer · v${VERSION}${R}"
  else
    echo -e "  ${CYAN}${B}J A R V I S${R}  ${HOLO}◉ ORB${R}"
    echo -e "  ${DIM}AI Brain + Visualizer · v${VERSION}${R}"
  fi
  echo ""
}

show_logo_done() {
  echo ""
  if command -v npx &>/dev/null; then
    npx -y oh-my-logo "JARVIS" --palette-colors "#8EE4FF,#B0F0FF,#8EE4FF" --filled --block-font block -d diagonal --color 2>/dev/null
    echo -e "                                  ${GREEN}${B}◉ ORB${R}"
    echo -e "                                  ${GREEN}ONLINE${R} ${DIM}· v${VERSION}${R}"
  else
    echo -e "  ${GREEN}${B}J A R V I S${R}  ${GREEN}◉ ORB${R}"
    echo -e "  ${GREEN}ONLINE${R} ${DIM}· v${VERSION}${R}"
  fi
  echo ""
}

# ── Helpers ──
STEP_NUM=0
TOTAL_STEPS=4

step() {
  STEP_NUM=$((STEP_NUM + 1))
  local filled=$((STEP_NUM * 20 / TOTAL_STEPS))
  local empty=$((20 - filled))
  local bar=""
  for i in $(seq 1 $filled); do bar="${bar}█"; done
  for i in $(seq 1 $empty); do bar="${bar}░"; done
  echo ""
  echo -e "  ${DIM}[${bar}] ${STEP_NUM}/${TOTAL_STEPS}${R}"
  echo -e "  ${CYAN}→${R} ${B}$1${R}"
}

info() { echo -e "    ${DIM}$1${R}"; }
ok() { echo -e "    ${GREEN}✓${R} $1"; }
warn() { echo -e "    ${YELLOW}!${R} $1"; }

# ── Detect ──
OS="$(uname -s)"
ARCH="$(uname -m)"
case "$OS" in
  Darwin) PLATFORM="macos" ;;
  Linux)  PLATFORM="linux" ;;
  MINGW*|MSYS*|CYGWIN*) PLATFORM="windows" ;;
  *) echo -e "  ${RED}Unsupported: $OS${R}"; exit 1 ;;
esac

# ── Apple Silicon check ──
if [ "$PLATFORM" = "macos" ] && [ "$ARCH" != "arm64" ]; then
  echo -e "  ${RED}Apple Silicon (M1+) required.${R}"
  echo -e "  ${DIM}Intel Mac is not supported. Jarvis Orb requires Apple Silicon (M1, M2, M3, M4).${R}"
  echo ""
  exit 1
fi

# ── Start ──
show_logo

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
  warn "No Python package manager"
  PIP_CMD=""
fi

# ── Step 2: Brain Lite ──
step "Installing Brain Lite"

mkdir -p "$BRAIN_DIR" "$BRAIN_BIN"

if [ -n "$PIP_CMD" ]; then
  $PIP_CMD --target "$BRAIN_DIR/lib" aiosqlite websockets mcp >/dev/null 2>&1 && \
    ok "Dependencies installed" || warn "Dependency install failed"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
if [ -d "$SCRIPT_DIR/brain/jarvis_brain" ]; then
  cp -r "$SCRIPT_DIR/brain/jarvis_brain" "$BRAIN_DIR/jarvis_brain"
  ok "Brain Lite → ~/.jarvis-orb/"
else
  curl -fsSL "https://github.com/$REPO/archive/refs/heads/main.tar.gz" 2>/dev/null | \
    tar -xz --strip-components=2 -C "$BRAIN_DIR" "jarvis-orb-main/brain/jarvis_brain" 2>/dev/null && \
    ok "Brain Lite downloaded" || warn "Download failed"
fi

cat > "$BRAIN_BIN/jarvis-brain" << 'EOF'
#!/bin/bash
export PYTHONPATH="$HOME/.jarvis-orb/lib:$HOME/.jarvis-orb"
exec python3 -m jarvis_brain.mcp_server "$@"
EOF
chmod +x "$BRAIN_BIN/jarvis-brain"

cat > "$BRAIN_BIN/jarvis-orb" << 'EOF'
#!/bin/bash
export PYTHONPATH="$HOME/.jarvis-orb/lib:$HOME/.jarvis-orb"
exec python3 -m jarvis_brain.cli "$@"
EOF
chmod +x "$BRAIN_BIN/jarvis-orb"
ok "Commands → jarvis-orb, jarvis-brain"

if [[ ":$PATH:" != *":$BRAIN_BIN:"* ]]; then
  SHELL_RC=""
  if [ -f "$HOME/.zshrc" ]; then SHELL_RC="$HOME/.zshrc"
  elif [ -f "$HOME/.bashrc" ]; then SHELL_RC="$HOME/.bashrc"
  fi
  if [ -n "$SHELL_RC" ]; then
    if ! grep -q "jarvis-orb/bin" "$SHELL_RC" 2>/dev/null; then
      echo 'export PATH="$HOME/.jarvis-orb/bin:$PATH"' >> "$SHELL_RC"
      ok "Added to PATH in $(basename $SHELL_RC)"
    fi
  fi
fi

# ── Step 3: Claude Code MCP ──
step "Configuring Claude Code"

if command -v claude &>/dev/null; then
  if claude mcp list 2>/dev/null | grep -q "jarvis-brain"; then
    ok "Already configured"
  else
    claude mcp add jarvis-brain \
      -e PYTHONPATH="$BRAIN_DIR/lib:$BRAIN_DIR" \
      -- python3 -m jarvis_brain.mcp_server 2>/dev/null && \
      ok "MCP server registered in Claude Code" || {
        info "Run manually:"
        echo -e "    ${WHITE}claude mcp add jarvis-brain -e PYTHONPATH=\"$BRAIN_DIR/lib:$BRAIN_DIR\" -- python3 -m jarvis_brain.mcp_server${R}"
      }
  fi
else
  info "Claude Code not found — install it first, then run installer again"
fi

# ── Step 4: Orb App ──
step "Installing Orb"

if [ "$PLATFORM" = "macos" ]; then
  LATEST=$(curl -fsSL "https://api.github.com/repos/$REPO/releases/latest" 2>/dev/null | \
    grep "browser_download_url.*aarch64.*dmg" | head -1 | cut -d'"' -f4)
  if [ -n "$LATEST" ]; then
    info "Downloading Orb for Apple Silicon..."
    if curl -fsSL -o "/tmp/JarvisOrb.dmg" "$LATEST"; then
      hdiutil attach "/tmp/JarvisOrb.dmg" -quiet -nobrowse 2>/dev/null
      if cp -r "/Volumes/Jarvis Orb/Jarvis Orb.app" "/Applications/" 2>/dev/null; then
        ok "Jarvis Orb.app → /Applications/"
      else
        warn "Could not copy to /Applications/ — try running with sudo"
      fi
      hdiutil detach "/Volumes/Jarvis Orb" -quiet 2>/dev/null || true
      rm -f "/tmp/JarvisOrb.dmg"
    else
      warn "Download failed — check your network connection"
    fi
  else
    warn "No release found — build: cd orb && pnpm install && cargo tauri build"
  fi
fi

# ── Done ──
show_logo_done

echo -e "  ${DIM}Brain${R}   ~/.jarvis-orb/brain.db"
echo -e "  ${DIM}MCP${R}     jarvis-brain"
echo -e "  ${DIM}Orb${R}     Jarvis Orb.app"
echo -e "  ${DIM}CLI${R}     jarvis-orb"
echo ""
echo -e "  ${CYAN}Your AI will start remembering.${R}"
echo -e "  ${DIM}Run ${WHITE}jarvis-orb${DIM} to begin.${R}"
echo ""
