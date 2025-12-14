import React, { createContext, useContext, useState, useCallback } from 'react';
import PropTypes from 'prop-types';

// السياق الرئيسي
const TankContext = createContext();

export const useTank = () => {
  const context = useContext(TankContext);
  if (!context) {
    throw new Error('useTank must be used within a TankProvider');
  }
  return context;
};

export const TankProvider = ({ children }) => {
  // حالة الخزان الرئيسية
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
    turbidity: 5.0,
    last_update: new Date().toISOString()
  });

  // التنبيهات
  const [alerts, setAlerts] = useState([]);
  
  // سجلات الذكاء الاصطناعي
  const [aiLogs, setAiLogs] = useState([]);
  
  // تاريخ البيانات
  const [history, setHistory] = useState([]);
  
  // حالة المحاكاة
  const [simulationState, setSimulationState] = useState({
    running: true,
    time_scale: 1.0,
    current_scenario: null,
    start_time: new Date().toISOString()
  });

  // تحديث حالة الخزان
  const updateTankState = useCallback((updates) => {
    setTankState(prev => ({
      ...prev,
      ...updates,
      last_update: new Date().toISOString()
    }));
    
    // إضافة إلى التاريخ
    setHistory(prev => {
      const newEntry = {
        ...tankState,
        ...updates,
        timestamp: new Date().toISOString()
      };
      
      // الاحتفاظ بآخر 1000 قراءة
      return [newEntry, ...prev.slice(0, 999)];
    });
  }, [tankState]);

  // إضافة تنبيه
  const addAlert = useCallback((alert) => {
    const newAlert = {
      ...alert,
      id: Date.now(),
      timestamp: new Date().toISOString(),
      acknowledged: false
    };
    
    setAlerts(prev => [newAlert, ...prev.slice(0, 49)]);
  }, []);

  // إضافة سجل ذكاء اصطناعي
  const addAILog = useCallback((log) => {
    const newLog = {
      ...log,
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString(),
      time: new Date().toLocaleTimeString()
    };
    
    setAiLogs(prev => [newLog, ...prev.slice(0, 49)]);
  }, []);

  // التعرف على تنبيه
  const acknowledgeAlert = useCallback((alertId) => {
    setAlerts(prev =>
      prev.map(alert =>
        alert.id === alertId ? { ...alert, acknowledged: true } : alert
      )
    );
  }, []);

  // مسح التنبيهات المعترف بها
  const clearAcknowledgedAlerts = useCallback(() => {
    setAlerts(prev => prev.filter(alert => !alert.acknowledged));
  }, []);

  // التحكم في المحاكاة
  const controlSimulation = useCallback((action, params = {}) => {
    switch (action) {
      case 'start':
        setSimulationState(prev => ({
          ...prev,
          running: true,
          start_time: new Date().toISOString()
        }));
        addAILog({
          message: '🚀 بدء المحاكاة',
          type: 'info'
        });
        break;
        
      case 'stop':
        setSimulationState(prev => ({
          ...prev,
          running: false
        }));
        addAILog({
          message: '⏹ إيقاف المحاكاة',
          type: 'info'
        });
        break;
        
      case 'pause':
        setSimulationState(prev => ({
          ...prev,
          running: false
        }));
        addAILog({
          message: '⏸ إيقاف مؤقت للمحاكاة',
          type: 'info'
        });
        break;
        
      case 'resume':
        setSimulationState(prev => ({
          ...prev,
          running: true
        }));
        addAILog({
          message: '▶️ استئناف المحاكاة',
          type: 'info'
        });
        break;
        
      case 'reset':
        setSimulationState({
          running: true,
          time_scale: 1.0,
          current_scenario: null,
          start_time: new Date().toISOString()
        });
        
        // إعادة ضبط الخزان
        setTankState({
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
          turbidity: 5.0,
          last_update: new Date().toISOString()
        });
        
        addAILog({
          message: '🔄 إعادة ضبط المحاكاة',
          type: 'info'
        });
        break;
        
      case 'set_scenario':
        setSimulationState(prev => ({
          ...prev,
          current_scenario: params.scenario,
          start_time: new Date().toISOString()
        }));
        addAILog({
          message: `📋 تحميل سيناريو: ${params.scenario}`,
          type: 'info'
        });
        break;
        
      case 'set_time_scale':
        setSimulationState(prev => ({
          ...prev,
          time_scale: params.scale
        }));
        addAILog({
          message: `⚡ تغيير سرعة المحاكاة إلى ${params.scale}x`,
          type: 'info'
        });
        break;
        
      default:
        console.warn(`Unknown simulation action: ${action}`);
    }
  }, [addAILog]);

  // الحصول على إحصائيات
  const getStats = useCallback(() => {
    const now = new Date();
    const lastHour = new Date(now.getTime() - 60 * 60 * 1000);
    
    const recentHistory = history.filter(
      entry => new Date(entry.timestamp) > lastHour
    );
    
    if (recentHistory.length === 0) {
      return {
        avg_water_level: tankState.water_level,
        min_water_level: tankState.water_level,
        max_water_level: tankState.water_level,
        stability_score: 100,
        active_alerts: alerts.filter(a => !a.acknowledged).length,
        total_ai_logs: aiLogs.length
      };
    }
    
    const waterLevels = recentHistory.map(entry => entry.water_level);
    const avgWaterLevel = waterLevels.reduce((a, b) => a + b, 0) / waterLevels.length;
    const minWaterLevel = Math.min(...waterLevels);
    const maxWaterLevel = Math.max(...waterLevels);
    
    // حساب درجة الاستقرار
    let stabilityScore = 100;
    if (waterLevels.length > 1) {
      const changes = [];
      for (let i = 1; i < waterLevels.length; i++) {
        changes.push(Math.abs(waterLevels[i] - waterLevels[i - 1]));
      }
      const avgChange = changes.reduce((a, b) => a + b, 0) / changes.length;
      stabilityScore = Math.max(0, 100 - (avgChange * 10));
    }
    
    return {
      avg_water_level: parseFloat(avgWaterLevel.toFixed(1)),
      min_water_level: parseFloat(minWaterLevel.toFixed(1)),
      max_water_level: parseFloat(maxWaterLevel.toFixed(1)),
      stability_score: parseFloat(stabilityScore.toFixed(1)),
      active_alerts: alerts.filter(a => !a.acknowledged).length,
      total_ai_logs: aiLogs.length,
      simulation_time: Math.floor((now - new Date(simulationState.start_time)) / 1000),
      history_points: history.length
    };
  }, [tankState.water_level, history, alerts, aiLogs, simulationState.start_time]);

  // الحصول على التنبيهات النشطة
  const getActiveAlerts = useCallback(() => {
    return alerts.filter(alert => !alert.acknowledged);
  }, [alerts]);

  // الحصول على سجلات الذكاء الاصطناعي الأخيرة
  const getRecentAILogs = useCallback((limit = 10) => {
    return aiLogs.slice(0, limit);
  }, [aiLogs]);

  // الحصول على التاريخ المحدد
  const getHistoryRange = useCallback((startTime, endTime, limit = 100) => {
    const start = startTime ? new Date(startTime) : new Date(0);
    const end = endTime ? new Date(endTime) : new Date();
    
    return history
      .filter(entry => {
        const entryTime = new Date(entry.timestamp);
        return entryTime >= start && entryTime <= end;
      })
      .slice(0, limit);
  }, [history]);

  // محاكاة تسرب المياه
  const simulateLeak = useCallback((active = true) => {
    updateTankState({ leak_detected: active });
    
    if (active) {
      addAlert({
        type: 'leak',
        severity: 'critical',
        message: '🚨 تسرب مياه مكتشف في الخزان!',
        details: { action: 'محاكاة' }
      });
      
      addAILog({
        message: '🧪 تفعيل محاكاة التسرب',
        type: 'warning'
      });
    } else {
      addAILog({
        message: '✅ إلغاء محاكاة التسرب',
        type: 'info'
      });
    }
  }, [updateTankState, addAlert, addAILog]);

  // قيمة السياق
  const contextValue = {
    // الحالة
    tankState,
    alerts,
    aiLogs,
    history,
    simulationState,
    
    // التحديث
    updateTankState,
    addAlert,
    addAILog,
    acknowledgeAlert,
    clearAcknowledgedAlerts,
    controlSimulation,
    simulateLeak,
    
    // الحصول على البيانات
    getStats,
    getActiveAlerts,
    getRecentAILogs,
    getHistoryRange,
    
    // اختصارات
    startSimulation: () => controlSimulation('start'),
    stopSimulation: () => controlSimulation('stop'),
    pauseSimulation: () => controlSimulation('pause'),
    resumeSimulation: () => controlSimulation('resume'),
    resetSimulation: () => controlSimulation('reset'),
    
    // حالات مشتقة
    isSimulationRunning: simulationState.running,
    hasActiveAlerts: alerts.some(alert => !alert.acknowledged),
    waterVolume: (tankState.water_level / 100) * tankState.capacity
  };

  return (
    <TankContext.Provider value={contextValue}>
      {children}
    </TankContext.Provider>
  );
};

TankProvider.propTypes = {
  children: PropTypes.node.isRequired
};

export default TankContext;