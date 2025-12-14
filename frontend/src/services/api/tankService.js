import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const tankService = {
  // الحصول على حالة الخزان الحالية
  async getTankState() {
    try {
      const response = await axios.get(`${API_BASE_URL}/tank/state`);
      return response.data.data;
    } catch (error) {
      console.error('Error fetching tank state:', error);
      throw error;
    }
  },

  // الحصول على تاريخ الخزان
  async getTankHistory(limit = 100, startTime = null, endTime = null) {
    try {
      const params = { limit };
      if (startTime) params.start_time = startTime;
      if (endTime) params.end_time = endTime;
      
      const response = await axios.get(`${API_BASE_URL}/tank/history`, { params });
      return response.data.data;
    } catch (error) {
      console.error('Error fetching tank history:', error);
      throw error;
    }
  },

  // تحديث حالة الخزان
  async updateTank(dt = 1.0) {
    try {
      const response = await axios.post(`${API_BASE_URL}/tank/update`, { dt });
      return response.data.data;
    } catch (error) {
      console.error('Error updating tank:', error);
      throw error;
    }
  },

  // الحصول على مقاييس الأداء
  async getMetrics() {
    try {
      const response = await axios.get(`${API_BASE_URL}/tank/metrics`);
      return response.data.data;
    } catch (error) {
      console.error('Error fetching metrics:', error);
      throw error;
    }
  },

  // التنبؤ بمستقبل مستوى المياه
  async predict() {
    try {
      const response = await axios.get(`${API_BASE_URL}/tank/predict`);
      return response.data.data;
    } catch (error) {
      console.error('Error predicting:', error);
      throw error;
    }
  },

  // كشف الشذوذ
  async getAnomalies() {
    try {
      const response = await axios.get(`${API_BASE_URL}/tank/anomalies`);
      return response.data.data;
    } catch (error) {
      console.error('Error fetching anomalies:', error);
      throw error;
    }
  },

  // الحصول على إحصائيات النظام
  async getSystemStats() {
    try {
      const response = await axios.get(`${API_BASE_URL}/system/stats`);
      return response.data.data;
    } catch (error) {
      console.error('Error fetching system stats:', error);
      return {
        tank_readings_count: 0,
        first_reading: null,
        last_reading: null,
        active_alerts: 0,
        ai_logs_count: 0,
        avg_water_level_24h: 0
      };
    }
  }
};

export default tankService;