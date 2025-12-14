import React from 'react';
import { 
  Thermometer, Gauge, Droplets, Wind, 
  Activity, Zap, TrendingUp, TrendingDown,
  AlertCircle, CheckCircle
} from 'lucide-react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const MetricsDashboard = ({ tankState }) => {
  const metrics = [
    {
      title: 'مستوى المياه',
      value: `${tankState.water_level.toFixed(1)}%`,
      icon: Droplets,
      color: 'blue',
      trend: tankState.water_level > 50 ? 'up' : 'down',
      unit: '%'
    },
    {
      title: 'درجة الحرارة',
      value: `${tankState.temperature.toFixed(1)}°C`,
      icon: Thermometer,
      color: 'red',
      trend: tankState.temperature > 25 ? 'up' : 'down',
      unit: '°C'
    },
    {
      title: 'الضغط',
      value: `${tankState.pressure.toFixed(3)}`,
      icon: Gauge,
      color: 'purple',
      trend: tankState.pressure > 1.0 ? 'up' : 'down',
      unit: 'بار'
    },
    {
      title: 'معدل التدفق',
      value: `${tankState.flow_rate}`,
      icon: Wind,
      color: 'green',
      trend: tankState.flow_rate > 20 ? 'up' : 'down',
      unit: 'لتر/د'
    }
  ];

  // بيانات المخطط (مثال)
  const chartData = {
    labels: ['10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00'],
    datasets: [
      {
        label: 'مستوى المياه',
        data: [65, 70, 68, 72, 75, 73, 74],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'درجة الحرارة',
        data: [24, 25, 26, 25.5, 26.5, 27, 26],
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        align: 'start',
        labels: {
          usePointStyle: true,
          padding: 20
        }
      }
    },
    scales: {
      y: {
        beginAtZero: false,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        }
      },
      x: {
        grid: {
          display: false
        }
      }
    }
  };

  // حالة النظام
  const getSystemStatus = () => {
    if (tankState.leak_detected) return { text: 'تسرب مياه', color: 'red', icon: AlertCircle };
    if (tankState.water_level < 20) return { text: 'منخفض', color: 'orange', icon: AlertCircle };
    if (tankState.water_level > 90) return { text: 'مرتفع', color: 'orange', icon: AlertCircle };
    return { text: 'مستقر', color: 'green', icon: CheckCircle };
  };

  const systemStatus = getSystemStatus();

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold text-gray-800">لوحة القياسات</h3>
        <div className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-full">
          <systemStatus.icon className={`text-${systemStatus.color}-500`} size={18} />
          <span className="font-medium">حالة النظام: {systemStatus.text}</span>
        </div>
      </div>

      {/* بطاقات القياسات */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {metrics.map((metric, index) => {
          const Icon = metric.icon;
          return (
            <div key={index} className="bg-gray-50 p-4 rounded-xl hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-3">
                <div className="p-2 bg-white rounded-lg">
                  <Icon className={`text-${metric.color}-500`} size={20} />
                </div>
                <div className="flex items-center gap-1">
                  {metric.trend === 'up' ? (
                    <TrendingUp className="text-green-500" size={16} />
                  ) : (
                    <TrendingDown className="text-red-500" size={16} />
                  )}
                </div>
              </div>
              <div className="text-2xl font-bold text-gray-900 mb-1">
                {metric.value}
              </div>
              <div className="text-sm text-gray-600">{metric.title}</div>
              <div className="text-xs text-gray-500 mt-1">{metric.unit}</div>
            </div>
          );
        })}
      </div>

      {/* مخطط الاتجاهات */}
      <div className="mb-8">
        <h4 className="font-medium text-gray-700 mb-4">اتجاهات البيانات</h4>
        <div className="h-64">
          <Line data={chartData} options={chartOptions} />
        </div>
      </div>

      {/* معلومات إضافية */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 bg-blue-50 rounded-xl">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="text-blue-500" size={18} />
            <span className="text-sm font-medium">وضع التشغيل</span>
          </div>
          <div className="text-lg font-bold">
            {tankState.ai_mode ? 'آلي' : 'يدوي'}
          </div>
        </div>

        <div className="p-4 bg-green-50 rounded-xl">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="text-green-500" size={18} />
            <span className="text-sm font-medium">الطاقة</span>
          </div>
          <div className="text-lg font-bold">
            {tankState.is_filling || tankState.is_draining ? 'نشط' : 'خامل'}
          </div>
        </div>

        <div className="p-4 bg-purple-50 rounded-xl">
          <div className="flex items-center gap-2 mb-2">
            <Gauge className="text-purple-500" size={18} />
            <span className="text-sm font-medium">الضغط النسبي</span>
          </div>
          <div className="text-lg font-bold">
            {((tankState.pressure - 1) * 100).toFixed(1)}%
          </div>
        </div>

        <div className="p-4 bg-yellow-50 rounded-xl">
          <div className="flex items-center gap-2 mb-2">
            <Droplets className="text-yellow-500" size={18} />
            <span className="text-sm font-medium">الحجم</span>
          </div>
          <div className="text-lg font-bold">
            {((tankState.water_level / 100) * 1000).toFixed(0)} لتر
          </div>
        </div>
      </div>
    </div>
  );
};

export default MetricsDashboard;