import React, { createContext, useContext, useState, useCallback } from 'react';
import PropTypes from 'prop-types';

const SimulationContext = createContext();

export const useSimulation = () => {
  const context = useContext(SimulationContext);
  if (!context) {
    throw new Error('useSimulation must be used within SimulationProvider');
  }
  return context;
};

export const SimulationProvider = ({ children }) => {
  const [simulationState, setSimulationState] = useState({
    running: false,
    timeScale: 1.0,
    currentScenario: null,
    startTime: null
  });

  const startSimulation = useCallback(() => {
    setSimulationState(prev => ({
      ...prev,
      running: true,
      startTime: new Date().toISOString()
    }));
  }, []);

  const stopSimulation = useCallback(() => {
    setSimulationState(prev => ({
      ...prev,
      running: false
    }));
  }, []);

  const resetSimulation = useCallback(() => {
    setSimulationState({
      running: false,
      timeScale: 1.0,
      currentScenario: null,
      startTime: null
    });
  }, []);

  return (
    <SimulationContext.Provider value={{
      simulationState,
      startSimulation,
      stopSimulation,
      resetSimulation
    }}>
      {children}
    </SimulationContext.Provider>
  );
};

SimulationProvider.propTypes = {
  children: PropTypes.node.isRequired
};

export default SimulationContext;

frontend/src/components/TankVisualization/Tank2D.jsx
frontend/src/components/TankVisualization/WaterLevelIndicator.jsx
frontend/src/components/ControlPanel/ManualControls.jsx
frontend/src/components/ControlPanel/AIControls.jsx
frontend/src/components/ControlPanel/SimulationControls.jsx
frontend/src/components/Dashboard/RealTimeCharts.jsx
frontend/src/components/Dashboard/SystemStatus.jsx
frontend/src/components/Alerts/NotificationCenter.jsx
frontend/src/components/Logs/SystemLogs.jsx