import React, { useState, useEffect, useContext } from 'react';
import { TankContext } from '../contexts/TankContext';
import { SimulationContext } from '../contexts/SimulationContext';
import Tank3D from './TankVisualization/Tank3D';
import Tank2D from './TankVisualization/Tank2D';
import WaterLevelIndicator from './TankVisualization/WaterLevelIndicator';
import ManualControls from './ControlPanel/ManualControls';
import AIControls from './ControlPanel/AIControls';
import SimulationControls from './ControlPanel/SimulationControls';
import MetricsDashboard from './Dashboard/MetricsDashboard';
import RealTimeCharts from './Dashboard/RealTimeCharts';
import SystemStatus from './Dashboard/SystemStatus';
import AlertSystem from './Alerts/AlertSystem';
import NotificationCenter from './Alerts/NotificationCenter';
import AILogViewer from './Logs/AILogViewer';
import SystemLogs from './Logs/SystemLogs';

import { 
  Droplets, Cpu, AlertTriangle, Settings, 
  BarChart3, Activity, Database 
} from 'lucide-react';

const WaterTankDigitalTwin = () => {
  const { tankState, updateTankState } = useContext(TankContext);
  const { simulationState, startSimulation, stopSimulation } = useContext(SimulationContext);
  
  const [activeTab, setActiveTab] = useState('dashboard');
  const [viewMode, setViewMode] = useState('3d'); // '3d' or '2d'
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-4">
      {/* شريط العنوان */}
      <header className="bg-white rounded-xl shadow-lg p-6 mb-6">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-blue-100 rounded-xl">
              <Droplets className="text-blue-600" size={32} />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                التوأم الرقمي - خزان المياه الذكي
              </h1>
              <p className="text-gray-600">محاكاة حية متزامنة مع الخزان الفعلي</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-sm text-gray-500">الحالة</div>
              <div className={`text-lg font-bold ${simulationState.running ? 'text-green-600' : 'text-red-600'}`}>
                {simulationState.running ? '🟢 نشط' : '🔴 متوقف'}
              </div>
            </div>
            <button
              onClick={() => simulationState.running ? stopSimulation() : startSimulation()}
              className={`px-6 py-3 rounded-xl font-semibold ${simulationState.running 
                ? 'bg-red-500 hover:bg-red-600 text-white' 
                : 'bg-green-500 hover:bg-green-600 text-white'}`}
            >
              {simulationState.running ? 'إيقاف المحاكاة' : 'بدء المحاكاة'}
            </button>
          </div>
        </div>
      </header>
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* الشريط الجانبي */}
        <div className="lg:col-span-1 space-y-6">
          {/* حالة النظام */}
          <SystemStatus />
          
          {/* التنبيهات */}
          <AlertSystem />
          
          {/* الإشعارات */}
          <NotificationCenter />
        </div>
        
        {/* المحتوى الرئيسي */}
        <div className="lg:col-span-3 space-y-6">
          {/* تباديل العرض */}
          <div className="bg-white rounded-xl shadow-lg p-4">
            <div className="flex justify-between items-center">
              <div className="flex space-x-2">
                {['dashboard', 'visualization', 'control', 'analytics', 'logs'].map(tab => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-4 py-2 rounded-lg font-medium ${activeTab === tab 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
                  >
                    {tab === 'dashboard' && 'لوحة التحكم'}
                    {tab === 'visualization' && 'التصور'}
                    {tab === 'control' && 'التحكم'}
                    {tab === 'analytics' && 'التحليلات'}
                    {tab === 'logs' && 'السجلات'}
                  </button>
                ))}
              </div>
              
              <div className="flex space-x-2">
                <button
                  onClick={() => setViewMode('3d')}
                  className={`px-3 py-2 rounded-lg ${viewMode === '3d' 
                    ? 'bg-blue-100 text-blue-600' 
                    : 'bg-gray-100 text-gray-600'}`}
                >
                  3D
                </button>
                <button
                  onClick={() => setViewMode('2d')}
                  className={`px-3 py-2 rounded-lg ${viewMode === '2d' 
                    ? 'bg-blue-100 text-blue-600' 
                    : 'bg-gray-100 text-gray-600'}`}
                >
                  2D
                </button>
              </div>
            </div>
          </div>
          
          {/* المحتوى حسب التبويب النشط */}
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              <MetricsDashboard />
              <RealTimeCharts />
            </div>
          )}
          
          {activeTab === 'visualization' && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold mb-6">تصور الخزان الرقمي</h2>
              <div className="h-[500px] rounded-xl overflow-hidden border-2 border-gray-200">
                {viewMode === '3d' ? <Tank3D /> : <Tank2D />}
              </div>
              <div className="mt-6">
                <WaterLevelIndicator />
              </div>
            </div>
          )}
          
          {activeTab === 'control' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="md:col-span-2">
                <ManualControls />
              </div>
              <div className="space-y-6">
                <AIControls />
                <SimulationControls />
              </div>
            </div>
          )}
          
          {activeTab === 'analytics' && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold mb-6">التحليلات المتقدمة</h2>
              <div className="h-[400px]">
                {/* سيتم إضافة المخططات المتقدمة هنا */}
                <div className="flex items-center justify-center h-full text-gray-500">
                  لوحة التحليلات المتقدمة قيد التطوير
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'logs' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <AILogViewer />
              <SystemLogs />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default WaterTankDigitalTwin;