import React, { useState } from 'react';
import { 
  Play, Pause, RotateCcw, Settings, Target, 
  Thermometer, Gauge, Zap, AlertTriangle,
  CloudRain, Cloud, Wind
} from 'lucide-react';

const ControlPanel = ({ 
  tankState, 
  onControlAction, 
  onSimulationControl,
  simulationActive 
}) => {
  const [config, setConfig] = useState({
    targetLevel: tankState.target_level || 80,
    flowRate: tankState.flow_rate || 20,
    aiMode: tankState.ai_mode || true
  });

  const handleConfigUpdate = () => {
    onControlAction('updateConfig', {
      target_level: config.targetLevel,
      flow_rate: config.flowRate
    });
  };

  const handleModeSwitch = () => {
    const newMode = !config.aiMode;
    setConfig(prev => ({ ...prev, aiMode: newMode }));
    onControlAction('switchMode', { ai_mode: newMode });
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-800">لوحة التحكم</h3>
        <div className="flex items-center gap-2">
          <Settings className="text-gray-500" size={20} />
          <span className="text-sm text-gray-600">الإعدادات</span>
        </div>
      </div>

      {/* التحكم في المحاكاة */}
      <div className="mb-6 p-4 bg-gray-50 rounded-xl">
        <h4 className="font-medium text-gray-700 mb-3">التحكم في المحاكاة</h4>
        <div className="grid grid-cols-3 gap-2">
          <button
            onClick={() => onSimulationControl('start')}
            disabled={simulationActive}
            className={`p-3 rounded-lg flex flex-col items-center justify-center ${
              simulationActive 
                ? 'bg-gray-200 text-gray-500' 
                : 'bg-green-500 hover:bg-green-600 text-white'
            }`}
          >
            <Play size={20} />
            <span className="text-xs mt-1">بدء</span>
          </button>
          <button
            onClick={() => onSimulationControl('stop')}
            disabled={!simulationActive}
            className={`p-3 rounded-lg flex flex-col items-center justify-center ${
              !simulationActive 
                ? 'bg-gray-200 text-gray-500' 
                : 'bg-red-500 hover:bg-red-600 text-white'
            }`}
          >
            <Pause size={20} />
            <span className="text-xs mt-1">إيقاف</span>
          </button>
          <button
            onClick={() => onSimulationControl('reset')}
            className="p-3 rounded-lg bg-blue-500 hover:bg-blue-600 text-white flex flex-col items-center justify-center"
          >
            <RotateCcw size={20} />
            <span className="text-xs mt-1">إعادة</span>
          </button>
        </div>
      </div>

      {/* إعدادات الخزان */}
      <div className="space-y-4 mb-6">
        <div>
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
            <Target size={16} />
            مستوى الهدف: {config.targetLevel}%
          </label>
          <input
            type="range"
            min="20"
            max="95"
            value={config.targetLevel}
            onChange={(e) => setConfig(prev => ({ ...prev, targetLevel: e.target.value }))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>20%</span>
            <span>50%</span>
            <span>80%</span>
            <span>95%</span>
          </div>
        </div>

        <div>
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
            <Zap size={16} />
            معدل التدفق: {config.flowRate} لتر/دقيقة
          </label>
          <input
            type="range"
            min="5"
            max="50"
            value={config.flowRate}
            onChange={(e) => setConfig(prev => ({ ...prev, flowRate: e.target.value }))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>5</span>
            <span>20</span>
            <span>35</span>
            <span>50</span>
          </div>
        </div>

        <button
          onClick={handleConfigUpdate}
          className="w-full py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition-colors"
        >
          تطبيق الإعدادات
        </button>
      </div>

      {/* التحكم اليدوي */}
      {!config.aiMode && (
        <div className="mb-6 p-4 bg-yellow-50 rounded-xl">
          <h4 className="font-medium text-gray-700 mb-3">التحكم اليدوي</h4>
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => onControlAction('fill')}
              disabled={tankState.is_filling}
              className="p-3 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <CloudRain size={20} />
              ملء
            </button>
            <button
              onClick={() => onControlAction('drain')}
              disabled={tankState.is_draining}
              className="p-3 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Cloud size={20} />
              تفريغ
            </button>
          </div>
          <button
            onClick={() => onControlAction('stop')}
            className="w-full mt-3 p-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
          >
            إيقاف الكل
          </button>
        </div>
      )}

      {/* تبديل الوضع */}
      <div className="p-4 bg-gray-50 rounded-xl">
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-medium text-gray-700">وضع التحكم</h4>
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            config.aiMode 
              ? 'bg-green-100 text-green-800' 
              : 'bg-yellow-100 text-yellow-800'
          }`}>
            {config.aiMode ? 'آلي' : 'يدوي'}
          </div>
        </div>
        <button
          onClick={handleModeSwitch}
          className="w-full py-3 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-xl font-semibold hover:from-purple-600 hover:to-purple-700 transition-all flex items-center justify-center gap-2"
        >
          <Wind size={20} />
          تبديل إلى {config.aiMode ? 'التحكم اليدوي' : 'التحكم الآلي'}
        </button>
      </div>

      {/* أدوات المحاكاة */}
      <div className="mt-6 pt-6 border-t">
        <h4 className="font-medium text-gray-700 mb-3">أدوات المحاكاة</h4>
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => onControlAction('simulateLeak')}
            className="p-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 flex items-center justify-center gap-2"
          >
            <AlertTriangle size={20} />
            تسرب
          </button>
          <button
            onClick={() => onControlAction('resetLeak')}
            className="p-3 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 flex items-center justify-center gap-2"
          >
            <RotateCcw size={20} />
            إعادة ضبط
          </button>
        </div>
      </div>
    </div>
  );
};

export default ControlPanel;