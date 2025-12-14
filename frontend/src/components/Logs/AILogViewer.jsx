import React, { useState } from 'react';
import { 
  Bot, Clock, Filter, Search, 
  AlertTriangle, Info, CheckCircle,
  ChevronDown, ChevronUp 
} from 'lucide-react';

const AILogViewer = ({ logs }) => {
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [expandedLog, setExpandedLog] = useState(null);

  const logTypes = [
    { id: 'all', label: 'الكل', icon: Bot },
    { id: 'action', label: 'إجراءات', icon: CheckCircle },
    { id: 'warning', label: 'تحذيرات', icon: AlertTriangle },
    { id: 'info', label: 'معلومات', icon: Info },
    { id: 'emergency', label: 'طوارئ', icon: AlertTriangle }
  ];

  const filteredLogs = logs.filter(log => {
    if (filter !== 'all' && log.type !== filter) return false;
    if (search && !log.message.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const getLogIcon = (type) => {
    switch (type) {
      case 'action': return CheckCircle;
      case 'warning': return AlertTriangle;
      case 'emergency': return AlertTriangle;
      case 'info': return Info;
      default: return Bot;
    }
  };

  const getLogColor = (type) => {
    switch (type) {
      case 'action': return 'green';
      case 'warning': return 'yellow';
      case 'emergency': return 'red';
      case 'info': return 'blue';
      default: return 'gray';
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Bot className="text-blue-600" size={20} />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-800">سجلات الذكاء الاصطناعي</h3>
            <p className="text-sm text-gray-600">
              {filteredLogs.length} سجل
            </p>
          </div>
        </div>
      </div>

      {/* أدوات التصفية والبحث */}
      <div className="mb-6 space-y-4">
        <div className="relative">
          <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="بحث في السجلات..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-4 pr-10 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex flex-wrap gap-2">
          {logTypes.map((type) => {
            const Icon = type.icon;
            const isActive = filter === type.id;
            return (
              <button
                key={type.id}
                onClick={() => setFilter(type.id)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Icon size={16} />
                {type.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* قائمة السجلات */}
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {filteredLogs.length === 0 ? (
          <div className="text-center py-8">
            <Bot className="mx-auto text-gray-400 mb-3" size={40} />
            <p className="text-gray-600">لا توجد سجلات حالياً</p>
            <p className="text-sm text-gray-500 mt-1">سيظهر هنا قرارات الذكاء الاصطناعي</p>
          </div>
        ) : (
          filteredLogs.map((log, index) => {
            const LogIcon = getLogIcon(log.type);
            const colorClass = `text-${getLogColor(log.type)}-500`;
            const bgClass = `bg-${getLogColor(log.type)}-100`;
            const isExpanded = expandedLog === index;

            return (
              <div
                key={index}
                className="border rounded-xl hover:shadow-md transition-shadow"
              >
                <div 
                  className="p-4 cursor-pointer"
                  onClick={() => setExpandedLog(isExpanded ? null : index)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <div className={`p-2 rounded-lg ${bgClass}`}>
                        <LogIcon className={colorClass} size={18} />
                      </div>
                      <div className="flex-1">
                        <p className="text-gray-900">{log.message}</p>
                        <div className="flex items-center gap-4 mt-2">
                          <div className="flex items-center gap-1 text-xs text-gray-500">
                            <Clock size={12} />
                            {log.timestamp}
                          </div>
                          <span className={`text-xs px-2 py-1 rounded-full ${bgClass} ${colorClass}`}>
                            {log.type}
                          </span>
                        </div>
                      </div>
                    </div>
                    {isExpanded ? (
                      <ChevronUp className="text-gray-400" size={20} />
                    ) : (
                      <ChevronDown className="text-gray-400" size={20} />
                    )}
                  </div>
                </div>

                {isExpanded && log.details && (
                  <div className="px-4 pb-4">
                    <div className="pt-4 border-t">
                      <h5 className="text-sm font-medium text-gray-700 mb-2">التفاصيل:</h5>
                      <pre className="text-xs text-gray-600 bg-gray-50 p-3 rounded-lg overflow-x-auto">
                        {JSON.stringify(log.details, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* الإحصائيات */}
      {filteredLogs.length > 0 && (
        <div className="mt-6 pt-6 border-t">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{logs.length}</div>
              <div className="text-sm text-gray-600">إجمالي السجلات</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {logs.filter(l => l.type === 'action').length}
              </div>
              <div className="text-sm text-gray-600">إجراءات</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">
                {logs.filter(l => l.type === 'warning').length}
              </div>
              <div className="text-sm text-gray-600">تحذيرات</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {logs.filter(l => l.type === 'emergency').length}
              </div>
              <div className="text-sm text-gray-600">طوارئ</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AILogViewer;