import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const simulationService = {
  // إدارة السيناريوهات
  async getScenarios() {
    try {
      const response = await axios.get(`${API_BASE_URL}/simulation/scenarios`);
      return response.data.data;
    } catch (error) {
      console.error('Error fetching scenarios:', error);
      return [];
    }
  },

  async getScenario(name) {
    try {
      const response = await axios.get(`${API_BASE_URL}/simulation/scenarios/${name}`);
      return response.data.data;
    } catch (error) {
      console.error('Error fetching scenario:', error);
      throw error;
    }
  },

  async runScenario(name, speed = 1.0) {
    try {
      const response = await axios.post(`${API_BASE_URL}/simulation/scenarios/${name}/run`, {
        speed
      });
      return response.data;
    } catch (error) {
      console.error('Error running scenario:', error);
      throw error;
    }
  },

  // تكوينات المحاكاة
  async getConfigs() {
    try {
      const response = await axios.get(`${API_BASE_URL}/simulation/configs`);
      return response.data.data;
    } catch (error) {
      console.error('Error fetching configs:', error);
      return {};
    }
  },

  async getConfig(name) {
    try {
      const response = await axios.get(`${API_BASE_URL}/simulation/configs/${name}`);
      return response.data.data;
    } catch (error) {
      console.error('Error fetching config:', error);
      throw error;
    }
  },

  async saveConfig(name, config) {
    try {
      const response = await axios.post(`${API_BASE_URL}/simulation/configs/${name}`, config);
      return response.data;
    } catch (error) {
      console.error('Error saving config:', error);
      throw error;
    }
  },

  // التحكم في المحاكاة
  async getSimulationStatus() {
    try {
      const response = await axios.get(`${API_BASE_URL}/simulation/status`);
      return response.data.data;
    } catch (error) {
      console.error('Error fetching simulation status:', error);
      return {
        running: false,
        current_time: new Date().toISOString(),
        time_scale: 1.0,
        iterations: 0
      };
    }
  },

  async controlSimulation(action) {
    try {
      const response = await axios.post(`${API_BASE_URL}/simulation/control`, { action });
      return response.data;
    } catch (error) {
      console.error('Error controlling simulation:', error);
      throw error;
    }
  },

  // بدء المحاكاة
  async startSimulation() {
    return this.controlSimulation('start');
  },

  // إيقاف المحاكاة
  async stopSimulation() {
    return this.controlSimulation('stop');
  },

  // إيقاف مؤقت للمحاكاة
  async pauseSimulation() {
    return this.controlSimulation('pause');
  },

  // إعادة المحاكاة
  async resetSimulation() {
    return this.controlSimulation('reset');
  },

  // تصدير بيانات المحاكاة
  async exportSimulation(format = 'json', includeHistory = true) {
    try {
      const response = await axios.post(`${API_BASE_URL}/simulation/export`, {
        format,
        include_history: includeHistory
      });
      return response.data.data;
    } catch (error) {
      console.error('Error exporting simulation:', error);
      throw error;
    }
  },

  // محاكاة تسرب (اختصار)
  async simulateLeak(active = true) {
    try {
      const response = await axios.post(`${API_BASE_URL}/control/simulate/leak`, { active });
      return response.data;
    } catch (error) {
      console.error('Error simulating leak:', error);
      throw error;
    }
  },

  // إعادة ضبط التسرب
  async resetLeak() {
    return this.simulateLeak(false);
  },

  // المحاكاة المتقدمة
  async runAdvancedSimulation(params) {
    try {
      const response = await axios.post(`${API_BASE_URL}/simulation/advanced`, params);
      return response.data;
    } catch (error) {
      console.error('Error running advanced simulation:', error);
      throw error;
    }
  },

  // تحليل النتائج
  async analyzeResults(simulationId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/simulation/${simulationId}/analysis`);
      return response.data.data;
    } catch (error) {
      console.error('Error analyzing results:', error);
      throw error;
    }
  },

  // مقارنة السيناريوهات
  async compareScenarios(scenarioIds) {
    try {
      const response = await axios.post(`${API_BASE_URL}/simulation/compare`, {
        scenarios: scenarioIds
      });
      return response.data.data;
    } catch (error) {
      console.error('Error comparing scenarios:', error);
      throw error;
    }
  }
};

export default simulationService;