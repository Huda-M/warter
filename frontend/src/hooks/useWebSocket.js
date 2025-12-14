import { useState, useEffect, useCallback, useRef } from 'react';
import realtimeService from '../services/websocket/realtimeService';

const useWebSocket = (url) => {
  const [lastMessage, setLastMessage] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('DISCONNECTED');
  const [messages, setMessages] = useState([]);
  const [subscriptions, setSubscriptions] = useState({
    tank_updates: false,
    alerts: false,
    ai_logs: false
  });
  
  const isMounted = useRef(true);

  // معالج الرسائل الواردة
  const handleMessage = useCallback((data) => {
    if (!isMounted.current) return;
    
    setLastMessage(JSON.stringify(data));
    
    // تخزين الرسالة في السجل
    setMessages(prev => {
      const newMessage = {
        ...data,
        timestamp: new Date().toISOString(),
        id: Date.now() + Math.random()
      };
      
      // الاحتفاظ بآخر 50 رسالة فقط
      return [newMessage, ...prev.slice(0, 49)];
    });
    
    // تحديث الحالة بناءً على نوع الرسالة
    switch (data.type) {
      case 'tank_update':
        // يمكن تحديث حالة الخزان هنا إذا لزم الأمر
        break;
      case 'alert':
        // يمكن إضافة التنبيهات إلى الحالة
        break;
      case 'ai_log':
        // يمكن تحديث سجلات الذكاء الاصطناعي
        break;
      default:
        // أنواع رسائل أخرى
        break;
    }
  }, []);

  // معالج تغيير حالة الاتصال
  const handleConnectionChange = useCallback(() => {
    if (!isMounted.current) return;
    setConnectionStatus(realtimeService.getConnectionStatus());
  }, []);

  // الاتصال بـ WebSocket
  const connect = useCallback(() => {
    if (!isMounted.current) return;
    
    // تسجيل الـ callbacks
    realtimeService.onMessage(handleMessage);
    realtimeService.onOpen(handleConnectionChange);
    realtimeService.onClose(handleConnectionChange);
    realtimeService.onError(handleConnectionChange);
    
    // بدء الاتصال
    realtimeService.connect(url);
  }, [url, handleMessage, handleConnectionChange]);

  // قطع الاتصال
  const disconnect = useCallback(() => {
    realtimeService.offMessage(handleMessage);
    realtimeService.offOpen(handleConnectionChange);
    realtimeService.offClose(handleConnectionChange);
    realtimeService.offError(handleConnectionChange);
    
    realtimeService.disconnect();
  }, [handleMessage, handleConnectionChange]);

  // إرسال رسالة
  const sendMessage = useCallback((message) => {
    return realtimeService.send(message);
  }, []);

  // الاشتراك في قناة
  const subscribe = useCallback((channel) => {
    if (!subscriptions[channel]) {
      let result;
      
      switch (channel) {
        case 'tank_updates':
          result = realtimeService.subscribeToTank();
          break;
        case 'alerts':
          result = realtimeService.subscribeToAlerts();
          break;
        case 'ai_logs':
          result = realtimeService.subscribeToAILogs();
          break;
        default:
          result = false;
      }
      
      if (result) {
        setSubscriptions(prev => ({ ...prev, [channel]: true }));
        return true;
      }
    }
    return false;
  }, [subscriptions]);

  // إلغاء الاشتراك من قناة
  const unsubscribe = useCallback((channel) => {
    if (subscriptions[channel]) {
      let result;
      
      switch (channel) {
        case 'tank_updates':
          result = realtimeService.unsubscribeFromTank();
          break;
        case 'alerts':
          result = realtimeService.unsubscribeFromAlerts();
          break;
        case 'ai_logs':
          result = realtimeService.unsubscribeFromAILogs();
          break;
        default:
          result = false;
      }
      
      if (result) {
        setSubscriptions(prev => ({ ...prev, [channel]: false }));
        return true;
      }
    }
    return false;
  }, [subscriptions]);

  // التحكم في الخزان عبر WebSocket
  const sendControlCommand = useCallback((command, params = {}) => {
    return realtimeService.sendControlCommand(command, params);
  }, []);

  // التحكم في المحاكاة عبر WebSocket
  const controlSimulation = useCallback((action, params = {}) => {
    return realtimeService.requestSimulationControl(action, params);
  }, []);

  // طلب تحديث البيانات
  const requestUpdate = useCallback((component = 'tank') => {
    return realtimeService.requestTankUpdate();
  }, []);

  // تنظيف عند فك التثبيت
  useEffect(() => {
    isMounted.current = true;
    connect();
    
    return () => {
      isMounted.current = false;
      disconnect();
    };
  }, [connect, disconnect]);

  // اشتراك تلقائي في القنوات المهمة
  useEffect(() => {
    if (connectionStatus === 'CONNECTED') {
      // اشترك في القنوات الافتراضية
      subscribe('tank_updates');
      subscribe('alerts');
      subscribe('ai_logs');
    }
  }, [connectionStatus, subscribe]);

  return {
    // الحالة
    lastMessage,
    messages,
    connectionStatus,
    subscriptions,
    
    // الاتصال
    connect,
    disconnect,
    reconnect: connect,
    
    // الإرسال
    sendMessage,
    sendControlCommand,
    controlSimulation,
    requestUpdate,
    
    // الاشتراك
    subscribe,
    unsubscribe,
    
    // حالة الاتصال
    isConnected: connectionStatus === 'CONNECTED',
    isConnecting: connectionStatus === 'CONNECTING',
    isDisconnected: connectionStatus === 'DISCONNECTED' || connectionStatus === 'CLOSED',
    
    // مرشحات الرسائل
    getTankUpdates: () => messages.filter(m => m.type === 'tank_update'),
    getAlerts: () => messages.filter(m => m.type === 'alert'),
    getAILogs: () => messages.filter(m => m.type === 'ai_log'),
    getSystemMessages: () => messages.filter(m => m.type === 'system'),
    
    // إحصائيات
    getMessageStats: () => ({
      total: messages.length,
      tank_updates: messages.filter(m => m.type === 'tank_update').length,
      alerts: messages.filter(m => m.type === 'alert').length,
      ai_logs: messages.filter(m => m.type === 'ai_log').length,
      other: messages.filter(m => !['tank_update', 'alert', 'ai_log'].includes(m.type)).length
    }),
    
    // مساعدة
    clearMessages: () => setMessages([])
  };
};

export default useWebSocket;