import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const controlService = {
  // تبديل وضع التحكم
  async switchMode(ai_mode = true) {
    try {
      const response = await axios.post(`${API_BASE_URL}/control/mode`, { ai_mode });
      return response.data;
    } catch (error) {
      console.error('Error switching mode:', error);
      throw error;
    }
  },

  // بدء عملية الملء
  async startFill() {
    try {
      const response = await axios.post(`${API_BASE_URL}/control/fill`);
      return response.data;
    } catch (error) {
      console.error('Error starting fill:', error);
      throw error;
    }
  },

  // بدء عملية التفريغ
  async startDrain() {
    try {
      const response = await axios.post(`${API_BASE_URL}/control/drain`);
      return response.data;
    } catch (error) {
      console.error('Error starting drain:', error);
      throw error;
    }
  },

  // إيقاف جميع العمليات
  async stopAll() {
    try {
      const response = await axios.post(`${API_BASE_URL}/control/stop`);
      return response.data;
    } catch (error) {
      console.error('Error stopping all:', error);
      throw error;
    }
  },

  // تحديث إعدادات التحكم
  async updateConfig(config) {
    try {
      const response = await axios.post(`${API_BASE_URL}/control/config`, config);
      return response.data;
    } catch (error) {
      console.error('Error updating config:', error);
      throw error;
    }
  },

  // الحصول على قرار الذكاء الاصطناعي
  async getAIDecision() {
    try {
      const response = await axios.get(`${API_BASE_URL}/control/ai/decision`);
      return response.data.decision;
    } catch (error) {
      console.error('Error getting AI decision:', error);
      throw error;
    }
  },

  // الحصول على سجلات الذكاء الاصطناعي
  async getAILogs(limit = 20) {
    try {
      const response = await axios.get(`${API_BASE_URL}/control/ai/logs`, {
        params: { limit }
      });
      return response.data.data;
    } catch (error) {
      console.error('Error getting AI logs:', error);
      throw error;
    }
  },

  // محاكاة التسرب
  async simulateLeak(active = true) {
    try {
      const response = await axios.post(`${API_BASE_URL}/control/simulate/leak`, { active });
      return response.data;
    } catch (error) {
      console.error('Error simulating leak:', error);
      throw error;
    }
  },

  // إعادة ضبط الخزان
  async resetTank() {
    try {
      const response = await axios.post(`${API_BASE_URL}/control/reset`);
      return response.data;
    } catch (error) {
      console.error('Error resetting tank:', error);
      throw error;
    }
  },

  // إدارة التنبيهات
  async getAlerts(unresolvedOnly = true, limit = 100, severity = null) {
    try {
      const params = { unresolved_only: unresolvedOnly, limit };
      if (severity) params.severity = severity;
      
      const response = await axios.get(`${API_BASE_URL}/alerts`, { params });
      return response.data.data;
    } catch (error) {
      console.error('Error getting alerts:', error);
      return [];
    }
  },

  async acknowledgeAlert(alertId) {
    try {
      const response = await axios.post(`${API_BASE_URL}/alerts/${alertId}/acknowledge`);
      return response.data;
    } catch (error) {
      console.error('Error acknowledging alert:', error);
      throw error;
    }
  },

  async clearAllAlerts() {
    try {
      const response = await axios.post(`${API_BASE_URL}/alerts/clear`);
      return response.data;
    } catch (error) {
      console.error('Error clearing alerts:', error);
      throw error;
    }
  }
};

export default controlService;