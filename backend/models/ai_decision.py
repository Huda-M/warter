import numpy as np
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class AIAction(Enum):
    FILL = "fill"
    DRAIN = "drain"
    STOP = "stop"
    ALERT = "alert"

@dataclass
class AIConfig:
    """تكوين الذكاء الاصطناعي"""
    target_level: float = 80.0
    tolerance: float = 1.0  # نسبة مئوية
    decision_interval: float = 2.0  # ثانية
    leak_threshold: float = 0.3  # انخفاض/ثانية
    prediction_horizon: int = 10  # خطوات تنبؤ
    learning_rate: float = 0.01

class AIDecisionMaker:
    """صانع قرارات الذكاء الاصطناعي"""
    
    def __init__(self, config: Optional[AIConfig] = None):
        self.config = config or AIConfig()
        self.logs = []
        self.patterns_learned = []
        self.last_action = None
        self.action_history = []
        
    def analyze(self, tank_state: Dict[str, Any], historical_data: list) -> Tuple[AIAction, str, dict]:
        """تحليل حالة الخزان واتخاذ القرار"""
        
        current_level = tank_state['water_level']
        is_filling = tank_state['is_filling']
        is_draining = tank_state['is_draining']
        leak_detected = tank_state['leak_detected']
        flow_rate = tank_state['flow_rate']
        
        # إذا كان هناك تسرب
        if leak_detected:
            log_msg = "🚨 حالة طوارئ: تسرب مياه مكتشف!"
            self._add_log(log_msg, "emergency")
            return AIAction.STOP, log_msg, {"emergency": True}
        
        # حساب الفرق عن الهدف
        level_diff = current_level - self.config.target_level
        
        # إذا كان ضمن نطاق التسامح
        if abs(level_diff) <= self.config.tolerance:
            if is_filling or is_draining:
                log_msg = f"⏹ الوصول للمستوى المطلوب ({current_level:.1f}%)"
                self._add_log(log_msg, "info")
                return AIAction.STOP, log_msg, {"status": "stable"}
            return AIAction.STOP, "مستقر", {"status": "stable"}
        
        # إذا كان أقل من الهدف
        if level_diff < -self.config.tolerance:
            if not is_filling:
                log_msg = f"📈 بدء الملء من {current_level:.1f}% إلى {self.config.target_level}%"
                self._add_log(log_msg, "action")
                return AIAction.FILL, log_msg, {
                    "reason": "below_target",
                    "difference": abs(level_diff)
                }
            else:
                # التحقق من كفاءة الملء
                efficiency = self._check_fill_efficiency(historical_data)
                if efficiency < 0.5:
                    log_msg = f"⚠️ كفاءة الملء منخفضة ({efficiency:.0%})"
                    self._add_log(log_msg, "warning")
                
        # إذا كان أعلى من الهدف
        else:
            if not is_draining:
                log_msg = f"📉 بدء التفريغ من {current_level:.1f}% إلى {self.config.target_level}%"
                self._add_log(log_msg, "action")
                return AIAction.DRAIN, log_msg, {
                    "reason": "above_target",
                    "difference": abs(level_diff)
                }
        
        # إذا كان هناك نشاط بالفعل، متابعة
        if is_filling:
            return AIAction.FILL, "متابعة الملء", {"status": "continuing"}
        elif is_draining:
            return AIAction.DRAIN, "متابعة التفريغ", {"status": "continuing"}
        
        return AIAction.STOP, "لا إجراء", {"status": "idle"}
    
    def predict_trend(self, historical_data: list, steps: int = 10) -> Dict[str, Any]:
        """التنبؤ باتجاه مستوى المياه"""
        if len(historical_data) < 5:
            return {"prediction": "insufficient_data", "confidence": 0}
        
        levels = [d['water_level'] for d in historical_data[-20:]]
        
        # تحليل بسيط للمتجهات
        if len(levels) >= 2:
            recent_change = levels[-1] - levels[-2]
            avg_change = np.mean(np.diff(levels[-5:])) if len(levels) >= 5 else recent_change
            
            # التنبؤ الخطي البسيط
            predicted_levels = []
            current = levels[-1]
            
            for i in range(steps):
                current += avg_change
                predicted_levels.append(max(0, min(100, current)))
            
            confidence = max(0, min(1, 1 - abs(avg_change)/10))
            
            return {
                "predicted_levels": predicted_levels,
                "trend": "increasing" if avg_change > 0 else "decreasing",
                "rate_of_change": round(avg_change, 3),
                "confidence": round(confidence, 2),
                "time_to_target": self._estimate_time_to_target(levels[-1], avg_change)
            }
        
        return {"prediction": "no_trend", "confidence": 0}
    
    def _estimate_time_to_target(self, current: float, rate: float) -> Optional[float]:
        """تقدير الوقت للوصول للهدف"""
        if abs(rate) < 0.001:
            return None
        
        diff = self.config.target_level - current
        time_seconds = abs(diff / rate) * 60  # تحويل من %/دقيقة إلى ثواني
        
        return round(time_seconds, 1)
    
    def _check_fill_efficiency(self, historical_data: list) -> float:
        """فحص كفاءة عملية الملء"""
        if len(historical_data) < 10:
            return 1.0
        
        recent = historical_data[-10:]
        levels = [d['water_level'] for d in recent]
        
        if len(levels) >= 2:
            actual_change = levels[-1] - levels[0]
            expected_change = 1.0  # تغيير متوقع في 10 قراءات
            
            efficiency = min(1.0, max(0, actual_change / expected_change))
            return efficiency
        
        return 1.0
    
    def detect_anomalies(self, tank_state: Dict[str, Any], historical_data: list) -> list:
        """كشف الشذوذ والأنماط غير الطبيعية"""
        anomalies = []
        
        # كشف تغيرات مفاجئة
        if len(historical_data) >= 3:
            recent = historical_data[-3:]
            changes = [recent[i+1]['water_level'] - recent[i]['water_level'] for i in range(len(recent)-1)]
            
            if any(abs(change) > 5 for change in changes):  # تغير أكثر من 5%
                anomalies.append({
                    "type": "sudden_change",
                    "severity": "high",
                    "message": "تغير مفاجئ في مستوى المياه"
                })
        
        # كشف درجات حرارة غير طبيعية
        if tank_state['temperature'] > 40:
            anomalies.append({
                "type": "high_temperature",
                "severity": "medium",
                "message": f"درجة حرارة عالية: {tank_state['temperature']}°C"
            })
        
        # كشف ضغط غير طبيعي
        if tank_state['pressure'] > 2.0:
            anomalies.append({
                "type": "high_pressure",
                "severity": "high",
                "message": f"ضغط عالٍ: {tank_state['pressure']} بار"
            })
        
        return anomalies
    
    def optimize_parameters(self, performance_data: list) -> Dict[str, float]:
        """تحسين معاملات التحكم بناءً على الأداء السابق"""
        if not performance_data:
            return {}
        
        # تحليل بسيط للأداء
        avg_error = np.mean([d.get('error', 0) for d in performance_data])
        avg_response_time = np.mean([d.get('response_time', 0) for d in performance_data])
        
        optimizations = {}
        
        # ضبط التسامح بناءً على الأداء
        if avg_error < 0.5:
            optimizations['tolerance'] = max(0.5, self.config.tolerance * 0.9)
        else:
            optimizations['tolerance'] = min(2.0, self.config.tolerance * 1.1)
        
        # ضبط معدل التدفق المقترح
        if avg_response_time > 60:  # إذا كان وقت الاستجابة طويلاً
            optimizations['suggested_flow_rate'] = min(50, self.config.target_level + 10)
        
        return optimizations
    
    def _add_log(self, message: str, log_type: str = "info"):
        """إضافة سجل"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "type": log_type
        }
        self.logs.append(log_entry)
        
        # الاحتفاظ بآخر 100 سجل فقط
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]
    
    def get_recent_logs(self, count: int = 10) -> list:
        """الحصول على أحدث السجلات"""
        return self.logs[-count:] if self.logs else []