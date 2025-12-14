import React from 'react';
import { TankProvider } from './contexts/TankContext';
import WaterTankDigitalTwin from './components/WaterTankDigitalTwin';

function App() {
  return (
    <TankProvider>
      <div className="App">
        <WaterTankDigitalTwin />
      </div>
    </TankProvider>
  );
}

export default App;