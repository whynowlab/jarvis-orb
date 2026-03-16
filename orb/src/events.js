/**
 * EventBridge — connects WebSocket events to Orb animations + log panel.
 */
export class EventBridge {
  constructor(orb, logPanel) {
    this.orb = orb;
    this.logPanel = logPanel;
    this.ws = null;
    this.reconnectInterval = 3000;
  }

  handleEvent(event) {
    // Trigger orb animation
    this.orb.triggerAnimation(event.type);

    // Add to log
    const tagMap = {
      memory_save: 'MEMORY',
      memory_contradict: 'ALERT',
      entity_update: 'ENTITY',
      team_dispatch: 'TEAM',
      team_result: 'TEAM',
      context_compact: 'COMPACT',
      session_start: 'SYSTEM',
      search: 'SEARCH',
      idle: 'IDLE',
    };
    const tag = tagMap[event.type] || 'EVENT';
    this.logPanel.addLine(tag, event.label || event.type);
  }

  connectWebSocket(url) {
    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log('[Orb] Connected to Brain');
        this.logPanel.addLine('SYSTEM', 'Connected to Jarvis Brain');
      };

      this.ws.onmessage = (msg) => {
        try {
          const event = JSON.parse(msg.data);
          this.handleEvent(event);
        } catch (e) {
          console.warn('[Orb] Invalid event:', msg.data);
        }
      };

      this.ws.onclose = () => {
        console.log('[Orb] Disconnected. Reconnecting...');
        setTimeout(() => this.connectWebSocket(url), this.reconnectInterval);
      };

      this.ws.onerror = () => {
        // Silent — will reconnect on close
      };
    } catch (e) {
      // WebSocket not available (demo mode)
      console.log('[Orb] Running in standalone mode');
    }
  }
}
