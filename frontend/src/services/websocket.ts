type WebSocketListener = (event: { type: string; data: any }) => void;

class WebSocketClient {
  private socket: WebSocket | null = null;
  private listeners: WebSocketListener[] = [];
  private reconnectInterval: number = 3000;
  private isExplicitlyClosed: boolean = false;
  private isConnected: boolean = false;

  constructor() {
    this.connect();
  }

  public connect() {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    let wsUrl = import.meta.env.VITE_WS_URL;
    if (!wsUrl) {
      const apiUrl = import.meta.env.VITE_API_URL;
      if (apiUrl) {
        const wsProto = apiUrl.startsWith('https:') ? 'wss:' : 'ws:';
        const cleanHost = apiUrl.replace(/^https?:\/\//, '').replace(/\/$/, '');
        wsUrl = `${wsProto}//${cleanHost}/ws`;
      } else {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        wsUrl = `${protocol}//${window.location.host}/ws`;
      }
    }

    try {
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        this.isConnected = true;
        this.notify({ type: 'system.connected', data: { connected: true } });
      };

      this.socket.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          this.notify(parsed);
        } catch {
          // ignore non-json messages (e.g. heartbeat)
        }
      };

      this.socket.onclose = () => {
        this.isConnected = false;
        this.notify({ type: 'system.disconnected', data: { connected: false } });
        if (!this.isExplicitlyClosed) {
          setTimeout(() => this.connect(), this.reconnectInterval);
        }
      };

      this.socket.onerror = () => {
        this.socket?.close();
      };
    } catch {
      setTimeout(() => this.connect(), this.reconnectInterval);
    }
  }

  public subscribe(listener: WebSocketListener): () => void {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  private notify(event: { type: string; data: any }) {
    for (const listener of this.listeners) {
      try {
        listener(event);
      } catch (e) {
        console.error('WebSocket listener error:', e);
      }
    }
  }

  public getStatus(): boolean {
    return this.isConnected;
  }
}

export const wsClient = new WebSocketClient();
