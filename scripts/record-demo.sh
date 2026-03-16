#!/bin/bash
# Jarvis Orb — Demo GIF Recorder
# Records the Orb window for 15 seconds → converts to GIF

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$PROJECT_DIR/assets"
BRAIN_DIR="$PROJECT_DIR/brain"
mkdir -p "$OUTPUT_DIR"

echo ""
echo "  Jarvis Orb — Demo Recorder"
echo ""

# Step 1: Start demo server
echo "  → Starting demo server..."
cd "$BRAIN_DIR"
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi
export PYTHONPATH="$BRAIN_DIR:$(find $BRAIN_DIR/.venv/lib -maxdepth 1 -name 'python*' | head -1)/site-packages"
python3 -m jarvis_brain.demo_server &
DEMO_PID=$!
sleep 2

# Step 2: Open Orb
echo "  → Opening Orb..."
ORB_APP="/Applications/Jarvis Orb.app"
[ ! -d "$ORB_APP" ] && ORB_APP="$PROJECT_DIR/orb/src-tauri/target/release/bundle/macos/Jarvis Orb.app"
open "$ORB_APP"
sleep 4

echo "  → Waiting for Orb to connect..."
sleep 3

# Step 3: Record with ffmpeg (macOS AVFoundation)
echo "  → Recording 15 seconds..."
RECORDING="$OUTPUT_DIR/demo-recording.mp4"

# List available screen devices
# ffmpeg -f avfoundation -list_devices true -i "" 2>&1

# Record screen (device 1 = screen, crop to orb area)
# Since we can't easily target the Orb window, record full screen then crop
ffmpeg -y \
  -f avfoundation \
  -framerate 30 \
  -i "1:none" \
  -t 15 \
  -vf "crop=300:300:0:0" \
  -c:v libx264 -preset ultrafast \
  "$RECORDING" \
  -loglevel error &
FFMPEG_PID=$!

echo "  → Recording... (15 seconds)"
echo "  → IMPORTANT: Move Orb window to top-left corner of screen!"
sleep 16

wait $FFMPEG_PID 2>/dev/null || true
echo "  ✓ Recording done"

# Step 4: Convert to GIF
echo "  → Converting to GIF..."
GIF_OUTPUT="$OUTPUT_DIR/demo.gif"

ffmpeg -y -i "$RECORDING" \
  -vf "fps=12,scale=300:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer" \
  -t 15 \
  "$GIF_OUTPUT" \
  -loglevel error

# Cleanup
rm -f "$RECORDING"
kill $DEMO_PID 2>/dev/null || true

SIZE=$(du -h "$GIF_OUTPUT" | cut -f1)
echo ""
echo "  ✓ Demo GIF: $GIF_OUTPUT ($SIZE)"
echo ""
