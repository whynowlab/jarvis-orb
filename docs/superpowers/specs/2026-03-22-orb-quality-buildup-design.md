# Orb Quality Buildup — Design Spec

**Date:** 2026-03-22
**Goal:** Stabilize + polish Orb desktop app before marketing push
**Scope:** UX fixes only. No new features, no MCP tool expansion.

## 1. Connection Status Visualization

**Problem:** Orb shows full animation even when Brain is disconnected.

**Solution:**
- Disconnected: Orb renders desaturated/gray, reduced displacement, dim glow
- Connected: Normal colors activate + green indicator dot at bottom
- Connection lost: Fade back to gray + red indicator dot
- Implementation: Add `connected` state to uniforms, CSS dot overlay

**Files:** `orb.js` (uniforms + gray mode), `events.js` (connection state), `index.html` (indicator dot CSS)

## 2. Remove Keyboard Demo Events

**Problem:** `main.js:27-42` has keydown handler that triggers fake events in production.

**Solution:** Delete the entire `document.addEventListener('keydown', ...)` block.

**File:** `main.js`

## 3. Right-Click Context Menu

**Problem:** No way to access settings or see status. No standard desktop app controls.

**Items:**
- Brain connection status (display only, green/red text)
- Log show/hide toggle
- Reset position (move window to default x:50, y:50)
- Run Doctor (opens terminal with `jarvis-orb --doctor`)
- Quit

**Implementation:** Tauri native menu via `Menu` API from `@tauri-apps/api`, triggered on `contextmenu` event.

**Files:** `main.js` (menu creation + event), `src-tauri/tauri.conf.json` (if permissions needed)

## 4. Log Panel Discoverability

**Problem:** Double-click to toggle log panel is invisible to new users.

**Solution:** On first Brain connection, show log panel for 3 seconds then auto-hide with a fade. User learns it exists. Subsequent connections don't repeat.

**Files:** `events.js` (first-connect logic), `log.js` (auto-hide timer)

## 5. Resize Handling

**Problem:** `orb.resize(w, h)` exists but is never called.

**Solution:** Add `window.addEventListener('resize', ...)` in `main.js`.

**File:** `main.js`

## Out of Scope

- Window position memory
- System tray
- Auto-update
- MCP tool expansion
- New animation types
- Settings/preferences UI
