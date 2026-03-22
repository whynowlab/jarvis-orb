/**
 * EventBridge — connects WebSocket events to Orb animations + log panel.
 */
export class EventBridge {
  constructor(orb, logPanel) {
    this.orb = orb;
    this.logPanel = logPanel;
    this.ws = null;
    this.connected = false;
    this.reconnectInterval = 3000;
    this._firstConnect = true;
    this._indicator = document.getElementById('connection-indicator');
  }

  _setConnected(state) {
    this.connected = state;
    this.orb.setConnected(state);
    if (this._indicator) {
      this._indicator.className = 'indicator ' + (state ? 'connected' : 'disconnected');
    }
  }

  handleEvent(event) {
    this.orb.triggerAnimation(event.type);

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
        this._setConnected(true);
        this.logPanel.addLine('SYSTEM', 'Connected to Jarvis Brain');

        // First connection: briefly show log panel so user knows it exists
        if (this._firstConnect) {
          this._firstConnect = false;
          this.logPanel.show();
          setTimeout(() => this.logPanel.hide(), 3000);
        }
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
        this._setConnected(false);
        setTimeout(() => this.connectWebSocket(url), this.reconnectInterval);
      };

      this.ws.onerror = () => {};
    } catch (e) {
      this._setConnected(false);
    }
  }
}
