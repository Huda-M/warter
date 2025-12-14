class RealtimeService {
  constructor() {
    this.socket = null;
    this.callbacks = {
      onMessage: [],
      onOpen: [],
      onClose: [],
      onError: []
    };
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 3000; // 3 ثواني
  }

  connect(url) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      console.log('WebSocket is already connected');
      return;
    }

    try {
      this.socket = new WebSocket(url || process.env.REACT_APP_WS_URL || 'ws://localhost:5000');

      this.socket.onopen = (event) => {
        console.log('WebSocket connection established');
        this.reconnectAttempts = 0;
        this.callbacks.onOpen.forEach(callback => callback(event));
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.callbacks.onMessage.forEach(callback => callback(data));
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.socket.onclose = (event) => {
        console.log('WebSocket connection closed:', event.code, event.reason);
        this.callbacks.onClose.forEach(callback => callback(event));
        
        // إعادة الاتصال التلقائي
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          setTimeout(() => {
            console.log(`Attempting to reconnect... (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`);
            this.reconnectAttempts++;
            this.connect(url);
          }, this.reconnectInterval);
        }
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.callbacks.onError.forEach(callback => callback(error));
      };

    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  send(message) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      if (typeof message !== 'string') {
        message = JSON.stringify(message);
      }
      this.socket.send(message);
      return true;
    } else {
      console.warn('WebSocket is not connected');
      return false;
    }
  }

  // تسجيل callbacks
  onMessage(callback) {
    this.callbacks.onMessage.push(callback);
  }

  onOpen(callback) {
    this.callbacks.onOpen.push(callback);
  }

  onClose(callback) {
    this.callbacks.onClose.push(callback);
  }

  onError(callback) {
    this.callbacks.onError.push(callback);
  }

  // إلغاء تسجيل callbacks
  offMessage(callback) {
    this.callbacks.onMessage = this.callbacks.onMessage.filter(cb => cb !== callback);
  }

  offOpen(callback) {
    this.callbacks.onOpen = this.callbacks.onOpen.filter(cb => cb !== callback);
  }

  offClose(callback) {
    this.callbacks.onClose = this.callbacks.onClose.filter(cb => cb !== callback);
  }

  offError(callback) {
    this.callbacks.onError = this.callbacks.onError.filter(cb => cb !== callback);
  }

  // الحصول على حالة الاتصال
  getConnectionStatus() {
    if (!this.socket) {
      return 'DISCONNECTED';
    }
    
    switch (this.socket.readyState) {
      case WebSocket.CONNECTING:
        return 'CONNECTING';
      case WebSocket.OPEN:
        return 'CONNECTED';
      case WebSocket.CLOSING:
        return 'CLOSING';
      case WebSocket.CLOSED:
        return 'CLOSED';
      default:
        return 'UNKNOWN';
    }
  }

  // طلبات خاصة بالمحاكاة
  requestTankUpdate() {
    return this.send({ type: 'request_update', payload: { component: 'tank' } });
  }

  subscribeToTank() {
    return this.send({ type: 'subscribe', payload: { channel: 'tank_updates' } });
  }

  subscribeToAlerts() {
    return this.send({ type: 'subscribe', payload: { channel: 'alerts' } });
  }

  subscribeToAILogs() {
    return this.send({ type: 'subscribe', payload: { channel: 'ai_logs' } });
  }

  unsubscribeFromTank() {
    return this.send({ type: 'unsubscribe', payload: { channel: 'tank_updates' } });
  }

  unsubscribeFromAlerts() {
    return this.send({ type: 'unsubscribe', payload: { channel: 'alerts' } });
  }

  unsubscribeFromAILogs() {
    return this.send({ type: 'unsubscribe', payload: { channel: 'ai_logs' } });
  }

  // التحكم عن بعد
  sendControlCommand(command, params = {}) {
    return this.send({
      type: 'control_command',
      payload: {
        command,
        params,
        timestamp: new Date().toISOString()
      }
    });
  }

  requestSimulationControl(action, params = {}) {
    return this.send({
      type: 'simulation_control',
      payload: {
        action,
        params,
        timestamp: new Date().toISOString()
      }
    });
  }
}

// إنشاء نسخة وحيدة من الخدمة (Singleton)
const realtimeService = new RealtimeService();

export default realtimeService;