import React, { useState } from 'react';
import { AlertTriangle, X, Bell, CheckCircle, Info } from 'lucide-react';

const AlertSystem = ({ alerts }) => {
  const [expanded, setExpanded] = useState(false);
  const [acknowledgedAlerts, setAcknowledgedAlerts] = useState([]);

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'red';
      case 'error': return 'orange';
      case 'warning': return 'yellow';
      case 'info': return 'blue';
      default: return 'gray';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
      case 'error':
        return AlertTriangle;
      case 'warning':
        return Bell;
      case 'info':
        return Info;
      default:
        return Info;
    }
  };

  const handleAcknowledge = (alertId) => {
    setAcknowledgedAlerts([...acknowledgedAlerts, alertId]);
  };

  const unacknowledgedAlerts = alerts.filter(
    alert => !acknowledgedAlerts.includes(alert.id)
  );

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-red-100 rounded-lg">
            <AlertTriangle className="text-red-600" size={20} />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-800">مركز التنبيهات</h3>
            <p className="text-sm text-gray-600">
              {unacknowledgedAlerts.length} تنبيه غير مقروء
            </p>
          </div>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
        >
          {expanded ? 'إخفاء' : 'عرض الكل'}
        </button>
      </div>

      {unacknowledgedAlerts.length === 0 ? (
        <div className="text-center py-8">
          <CheckCircle className="mx-auto text-green-500 mb-3" size={40} />
          <p className="text-gray-600">لا توجد تنبيهات حالياً</p>
          <p className="text-sm text-gray-500 mt-1">النظام يعمل بشكل طبيعي</p>
        </div>
      ) : (
        <div className="space-y-3">
          {(expanded ? unacknowledgedAlerts : unacknowledgedAlerts.slice(0, 3)).map((alert) => {
            const SeverityIcon = getSeverityIcon(alert.severity);
            const colorClass = `text-${getSeverityColor(alert.severity)}-500`;
            
            return (
              <div
                key={alert.id || alert.timestamp}
                className="p-4 border rounded-xl hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded-lg bg-${getSeverityColor(alert.severity)}-100`}>
                      <SeverityIcon className={colorClass} size={18} />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">{alert.title || 'تنبيه النظام'}</h4>
                      <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                      <div className="flex items-center gap-4 mt-2">
                        <span className="text-xs text-gray-500">
                          {new Date(alert.timestamp).toLocaleTimeString()}
                        </span>
                        <span className={`text-xs px-2 py-1 rounded-full bg-${getSeverityColor(alert.severity)}-100 text-${getSeverityColor(alert.severity)}-800`}>
                          {alert.severity}
                        </span>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => handleAcknowledge(alert.id || alert.timestamp)}
                    className="p-1 hover:bg-gray-100 rounded"
                  >
                    <X size={16} className="text-gray-500" />
                  </button>
                </div>
                
                {alert.details && expanded && (
                  <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                    <pre className="text-xs text-gray-600 whitespace-pre-wrap">
                      {JSON.stringify(alert.details, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {unacknowledgedAlerts.length > 3 && !expanded && (
        <button
          onClick={() => setExpanded(true)}
          className="w-full mt-4 py-2 text-center text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          عرض {unacknowledgedAlerts.length - 3} تنبيه إضافي
        </button>
      )}

      {acknowledgedAlerts.length > 0 && expanded && (
        <div className="mt-6 pt-6 border-t">
          <h4 className="font-medium text-gray-700 mb-3">التنبيهات المقروءة</h4>
          <div className="text-center py-4">
            <CheckCircle className="mx-auto text-gray-400 mb-2" size={24} />
            <p className="text-gray-500 text-sm">
              {acknowledgedAlerts.length} تنبيه تمت قراءته
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default AlertSystem;