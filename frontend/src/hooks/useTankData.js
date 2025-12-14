import { useState, useEffect, useCallback } from 'react';
import tankService from '../services/api/tankService';
import controlService from '../services/api/controlService';
import simulationService from '../services/api/simulationService';

const useTankData = (updateInterval = 2000) => {
  const [tankState, setTankState] = useState({
    water_level: 60,
    temperature: 25,
    pressure: 1.0,
    flow_rate: 20,
    is_filling: false,
    is_draining: false,
    leak_detected: false,
    ai_mode: true,
    target_level: 80,
    water_volume: 600,
    capacity: 1000,
    ph_level: 7.0,
    turbidity: 5.0
  });

  const [alerts, setAlerts] = useState([]);
  const [aiLogs, setAiLogs] = useState([]);
  const [metrics, setMetrics] = useState({});
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [simulationStatus, setSimulationStatus] = useState({
    running: true,
    time_scale: 1.0
  });

  // جلب البيانات الأولية
  const fetchInitialData = useCallback(async () => {
    try {
      setLoading(true);
      
      // جلب حالة الخزان
      const tankData = await tankService.getTankState();
      setTankState(tankData);
      
      // جلب مقاييس الأداء
      const metricsData = await tankService.getMetrics();
      setMetrics(metricsData);
      
      // جلب السجلات
      const logsData = await controlService.getAILogs(20);
      setAiLogs(logsData);
      
      // جلب التاريخ
      const historyData = await tankService.getTankHistory(50);
      setHistory(historyData);
      
      // جلب حالة المحاكاة
      const simStatus = await simulationService.getSimulationStatus();
      setSimulationStatus(simStatus);
      
      setError(null);
    } catch (err) {
      console.error('Error fetching initial data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // تحديث البيانات بشكل دوري
  useEffect(() => {
    fetchInitialData();
    
    const intervalId = setInterval(async () => {
      try {
        const tankData = await tankService.getTankState();
        setTankState(tankData);
      } catch (err) {
        console.error('Error updating tank data:', err);
      }
    }, updateInterval);

    return () => clearInterval(intervalId);
  }, [fetchInitialData, updateInterval]);

  // جلب التنبيهات
  const fetchAlerts = useCallback(async () => {
    try {
      const alertsData = await controlService.getAlerts(true, 10);
      setAlerts(alertsData);
    } catch (err) {
      console.error('Error fetching alerts:', err);
    }
  }, []);

  // تحديث سجلات الذكاء الاصطناعي
  const updateAILogs = useCallback(async () => {
    try {
      const logsData = await controlService.getAILogs(5);
      setAiLogs(prev => [...logsData, ...prev.slice(0, 15)]);
    } catch (err) {
      console.error('Error updating AI logs:', err);
    }
  }, []);

  // تنبؤ المستوى
  const predictLevel = useCallback(async () => {
    try {
      const prediction = await tankService.predict();
      return prediction;
    } catch (err) {
      console.error('Error predicting level:', err);
      return null;
    }
  }, []);

  // كشف الشذوذ
  const detectAnomalies = useCallback(async () => {
    try {
      const anomalies = await tankService.getAnomalies();
      return anomalies;
    } catch (err) {
      console.error('Error detecting anomalies:', err);
      return [];
    }
  }, []);

  // التحكم في الخزان
  const controlTank = useCallback(async (action, params = {}) => {
    try {
      let result;
      
      switch (action) {
        case 'fill':
          result = await controlService.startFill();
          break;
        case 'drain':
          result = await controlService.startDrain();
          break;
        case 'stop':
          result = await controlService.stopAll();
          break;
        case 'updateConfig':
          result = await controlService.updateConfig(params);
          break;
        case 'switchMode':
          result = await controlService.switchMode(params.ai_mode);
          break;
        case 'simulateLeak':
          result = await controlService.simulateLeak(params.active);
          break;
        case 'resetLeak':
          result = await controlService.simulateLeak(false);
          break;
        case 'reset':
          result = await controlService.resetTank();
          break;
        default:
          throw new Error(`Unknown action: ${action}`);
      }
      
      // تحديث البيانات بعد التحكم
      await fetchInitialData();
      return result;
      
    } catch (err) {
      console.error(`Error controlling tank (${action}):`, err);
      throw err;
    }
  }, [fetchInitialData]);

  // التحكم في المحاكاة
  const controlSimulation = useCallback(async (action) => {
    try {
      const result = await simulationService.controlSimulation(action);
      
      // تحديث حالة المحاكاة
      const simStatus = await simulationService.getSimulationStatus();
      setSimulationStatus(simStatus);
      
      return result;
    } catch (err) {
      console.error(`Error controlling simulation (${action}):`, err);
      throw err;
    }
  }, []);

  // تشغيل سيناريو
  const runScenario = useCallback(async (name, speed = 1.0) => {
    try {
      const result = await simulationService.runScenario(name, speed);
      await fetchInitialData();
      return result;
    } catch (err) {
      console.error(`Error running scenario (${name}):`, err);
      throw err;
    }
  }, [fetchInitialData]);

  // تصدير البيانات
  const exportData = useCallback(async (format = 'json', includeHistory = true) => {
    try {
      const result = await simulationService.exportSimulation(format, includeHistory);
      return result;
    } catch (err) {
      console.error('Error exporting data:', err);
      throw err;
    }
  }, []);

  return {
    tankState,
    setTankState,
    alerts,
    aiLogs,
    metrics,
    history,
    loading,
    error,
    simulationStatus,
    
    // الوظائف
    fetchInitialData,
    fetchAlerts,
    updateAILogs,
    predictLevel,
    detectAnomalies,
    controlTank,
    controlSimulation,
    runScenario,
    exportData,
    
    // اختصارات للتحكم
    startFill: () => controlTank('fill'),
    startDrain: () => controlTank('drain'),
    stopAll: () => controlTank('stop'),
    updateConfig: (config) => controlTank('updateConfig', config),
    switchMode: (aiMode) => controlTank('switchMode', { ai_mode: aiMode }),
    simulateLeak: (active = true) => controlTank('simulateLeak', { active }),
    resetLeak: () => controlTank('resetLeak'),
    resetTank: () => controlTank('reset'),
    
    // اختصارات للمحاكاة
    startSimulation: () => controlSimulation('start'),
    stopSimulation: () => controlSimulation('stop'),
    pauseSimulation: () => controlSimulation('pause'),
    resetSimulation: () => controlSimulation('reset')
  };
};

export default useTankData;