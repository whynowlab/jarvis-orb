import { createOrb } from './orb.js';
import { EventBridge } from './events.js';
import { LogPanel } from './log.js';

// Initialize
const canvas = document.getElementById('orb-canvas');
const logPanel = new LogPanel(document.getElementById('log-panel'));
const orb = createOrb(canvas);
const bridge = new EventBridge(orb, logPanel);

// Click to toggle log
canvas.addEventListener('click', () => logPanel.toggle());

// Keyboard demo (for development)
document.addEventListener('keydown', (e) => {
  const demoEvents = {
    '1': { type: 'memory_save', label: '결정: SQLite 유지', tier: 'semantic' },
    '2': { type: 'memory_contradict', label: '모순 감지: 이전 기억과 충돌' },
    '3': { type: 'entity_update', label: 'jarvis-brain: planning → implementing' },
    '4': { type: 'team_dispatch', label: 'strategy 팀 3명 투입' },
    '5': { type: 'team_result', label: '팀 결과 수신: CONDITIONAL GO' },
    '6': { type: 'context_compact', label: '컨텍스트 73% → 압축 실행' },
    '7': { type: 'session_start', label: 'Session initialized' },
    '8': { type: 'search', label: '메모리 검색: "auth module"' },
    '0': { type: 'idle', label: 'Idle' },
  };
  if (demoEvents[e.key]) {
    bridge.handleEvent(demoEvents[e.key]);
  }
});

// WebSocket connection (optional — for Brain Lite)
bridge.connectWebSocket('ws://localhost:9321');

// Start render loop
orb.animate();
