import { getCurrentWindow } from '@tauri-apps/api/window';
import { createOrb } from './orb.js';
import { EventBridge } from './events.js';
import { LogPanel } from './log.js';

// Initialize
const canvas = document.getElementById('orb-canvas');
const logPanel = new LogPanel(document.getElementById('log-panel'));
const orb = createOrb(canvas);
const bridge = new EventBridge(orb, logPanel);

// Window drag — manual implementation for decoration-less window
const dragRegion = document.getElementById('drag-region');
const appWindow = getCurrentWindow();

dragRegion.addEventListener('mousedown', async (e) => {
  if (e.detail === 2) {
    logPanel.toggle();
    return;
  }
  await appWindow.startDragging();
});

// Resize handling
window.addEventListener('resize', () => {
  orb.resize(window.innerWidth, window.innerHeight);
});

// Context menu
const ctxMenu = document.getElementById('ctx-menu');
const ctxStatus = document.getElementById('ctx-status');

dragRegion.addEventListener('contextmenu', (e) => {
  e.preventDefault();
  ctxStatus.textContent = bridge.connected ? '● Brain Connected' : '○ Brain Disconnected';
  ctxStatus.className = 'ctx-item ctx-status ' + (bridge.connected ? 'connected' : 'disconnected');
  ctxMenu.style.left = Math.min(e.clientX, window.innerWidth - 160) + 'px';
  ctxMenu.style.top = Math.min(e.clientY, window.innerHeight - 140) + 'px';
  ctxMenu.classList.add('visible');
});

document.addEventListener('click', () => {
  ctxMenu.classList.remove('visible');
});

document.getElementById('ctx-log').addEventListener('click', () => {
  logPanel.toggle();
});

document.getElementById('ctx-reset-pos').addEventListener('click', async () => {
  const { LogicalPosition } = await import('@tauri-apps/api/dpi');
  await appWindow.setPosition(new LogicalPosition(50, 50));
});

document.getElementById('ctx-quit').addEventListener('click', async () => {
  await appWindow.close();
});

// WebSocket connection (optional — for Brain Lite)
bridge.connectWebSocket('ws://localhost:9321');

// Start render loop
orb.animate();
