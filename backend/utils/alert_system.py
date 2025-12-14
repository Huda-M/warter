from datetime import datetime
from typing import Dict, Any, List
import logging
from .data_logger import DataLogger

logger = logging.getLogger(__name__)

class AlertSystem:
    def __init__(self, data_logger: DataLogger):
        self.data_logger = data_logger
        self.alert_rules = self._load_alert_rules()
    
    def _load_alert_rules(self) -> List[Dict]:
        """تحميل قواعد التنبيه"""
        return [
            {
                "name": "low_water_level",
                "condition": lambda state: state['water_level'] < 20,
                "severity": "high",
                "message": "مستوى المياه منخفض جداً!"
            },
            {
                "name": "high_water_level",
                "condition": lambda state: state['water_level'] > 90,
                "severity": "high",
                "message": "مستوى المياه مرتفع جداً!"
            },
            {
                "name": "high_temperature",
                "condition": lambda state: state['temperature'] > 40,
                "severity": "medium",
                "message": f"درجة حرارة عالية: {{temperature}}°C"
            },
            {
                "name": "low_temperature",
                "condition": lambda state: state['temperature'] < 5,
                "severity": "medium",
                "message": f"درجة حرارة منخفضة: {{temperature}}°C"
            },
            {
                "name": "high_pressure",
                "condition": lambda state: state['pressure'] > 2.0,
                "severity": "high",
                "message": f"ضغط عالٍ: {{pressure}} بار"
            },
            {
                "name": "ph_out_of_range",
                "condition": lambda state: state['ph_level'] < 6.5 or state['ph_level'] > 8.5,
                "severity": "medium",
                "message": f"الأس الهيدروجيني خارج النطاق: {{ph_level}}"
            },
            {
                "name": "leak_detected",
                "condition": lambda state: state['leak_detected'],
                "severity": "critical",
                "message": "تسرب مياه مكتشف!"
            }
        ]
    
    def check_alerts(self, tank_state: Dict[str, Any]) -> List[Dict]:
        """فحص حالة الخزان مقابل قواعد التنبيه"""
        triggered_alerts = []
        
        for rule in self.alert_rules:
            try:
                if rule['condition'](tank_state):
                    # تنسيق الرسالة
                    message = rule['message'].format(**tank_state)
                    
                    alert = {
                        "type": rule['name'],
                        "severity": rule['severity'],
                        "message": message,
                        "timestamp": datetime.now().isoformat(),
                        "data": tank_state
                    }
                    
                    triggered_alerts.append(alert)
                    
                    # تسجيل التنبيه في قاعدة البيانات
                    self.data_logger.log_alert(
                        rule['name'],
                        rule['severity'],
                        message
                    )
                    
                    logger.warning(f"Alert triggered: {rule['name']} - {message}")
            except Exception as e:
                logger.error(f"Error checking alert rule {rule['name']}: {e}")
        
        return triggered_alerts
    
    def get_active_alerts(self) -> List[Dict]:
        """الحصول على التنبيهات النشطة (غير المحلولة)"""
        return self.data_logger.get_alerts(unresolved_only=True)
    
    def acknowledge_alert(self, alert_id: int) -> bool:
        """التعرف على تنبيه (تعليمه كمقروء)"""
        try:
            self.data_logger.resolve_alert(alert_id)
            return True
        except Exception as e:
            logger.error(f"Error acknowledging alert {alert_id}: {e}")
            return False
    
    # ❌ المشكلة: دالة clear_all_alerts() غير موجودة
    def clear_all_alerts(self):
        conn = sqlite3.connect(self.data_logger.db_path)
        cursor = conn.cursor()
    
        cursor.execute('UPDATE alerts SET resolved = TRUE')
    
        conn.commit()
        conn.close()
    
        logger.info("All alerts cleared")