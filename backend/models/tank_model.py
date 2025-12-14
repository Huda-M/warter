import numpy as np
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class TankConfig:
    """تكوين الخزان"""
    max_capacity: float = 1000.0  # لتر
    min_capacity: float = 0.0
    initial_level: float = 60.0  # نسبة مئوية
    diameter: float = 1.5  # متر
    height: float = 2.0  # متر
    material: str = "steel"
    insulation_factor: float = 0.8

class WaterTank:
    """نموذج الخزان المادي"""
    
    def __init__(self, config: Optional[TankConfig] = None):
        self.config = config or TankConfig()
        
        # حالة الخزان
        self.water_level = self.config.initial_level  # نسبة مئوية
        self.water_volume = self._level_to_volume(self.water_level)  # لتر
        self.temperature = 25.0  # درجة مئوية
        self.pressure = 1.0  # بار
        self.ph_level = 7.0
        self.turbidity = 5.0  # NTU
        self.is_filling = False
        self.is_draining = False
        self.leak_detected = False
        self.flow_rate = 20.0  # لتر/دقيقة
        
        # سجلات
        self.history = []
        self.last_update = datetime.now()
        
    def _level_to_volume(self, level: float) -> float:
        """تحويل المستوى النسبي إلى حجم مطلق"""
        return (level / 100) * self.config.max_capacity
    
    def _volume_to_level(self, volume: float) -> float:
        """تحويل الحجم المطلق إلى مستوى نسبي"""
        return (volume / self.config.max_capacity) * 100
    
    def update_physics(self, dt: float = 1.0):
        """تحديث الفيزياء مع مرور الوقت"""
        # تأثيرات الحرارة
        ambient_temp = 20.0
        temp_diff = ambient_temp - self.temperature
        self.temperature += temp_diff * 0.01 * dt
        
        # تأثير التبخر
        evaporation_rate = 0.05 * (self.temperature / 30)  # لتر/ساعة
        volume_loss = (evaporation_rate / 3600) * dt
        
        # تأثير التسرب إذا كان موجوداً
        if self.leak_detected:
            leak_rate = 5.0  # لتر/دقيقة
            volume_loss += (leak_rate / 60) * dt
        
        # تحديث الحجم
        if self.is_filling:
            fill_rate = self.flow_rate / 60  # لتر/ثانية
            self.water_volume += fill_rate * dt
        elif self.is_draining:
            drain_rate = self.flow_rate / 60
            self.water_volume -= drain_rate * dt
        
        # تطبيق الخسائر
        self.water_volume = max(0, self.water_volume - volume_loss)
        
        # تحديث المستوى
        self.water_level = self._volume_to_level(self.water_volume)
        
        # حساب الضغط (P = ρgh)
        water_density = 1000  # كجم/م³
        gravity = 9.81  # م/ث²
        water_height = (self.water_volume / 1000) / (np.pi * (self.config.diameter/2)**2)
        self.pressure = 1.0 + (water_density * gravity * water_height) / 100000  # بار
        
        # تحديث جودة المياه
        self.ph_level += np.random.uniform(-0.01, 0.01)
        self.ph_level = max(6.5, min(8.5, self.ph_level))
        
        self.turbidity += np.random.uniform(-0.1, 0.1)
        self.turbidity = max(0, min(100, self.turbidity))
        
        # حفظ التاريخ
        self.history.append({
            'timestamp': datetime.now(),
            'water_level': self.water_level,
            'temperature': self.temperature,
            'pressure': self.pressure,
            'ph_level': self.ph_level,
            'turbidity': self.turbidity
        })
        
        # الاحتفاظ بآخر 1000 قراءة فقط
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        
        self.last_update = datetime.now()
        return self.get_state()
    
    def set_fill(self, fill: bool):
        """تفعيل/إلغاء الملء"""
        self.is_filling = fill
        if fill:
            self.is_draining = False
    
    def set_drain(self, drain: bool):
        """تفعيل/إلغاء التفريغ"""
        self.is_draining = drain
        if drain:
            self.is_filling = False
    
    def set_flow_rate(self, rate: float):
        """تعيين معدل التدفق"""
        self.flow_rate = max(5, min(50, rate))
    
    def set_target_level(self, target: float):
        """تعيين مستوى الهدف"""
        # يتم التحكم به من خلال الـ AI
    
    def simulate_leak(self, active: bool = True):
        """محاكاة تسرب المياه"""
        self.leak_detected = active
        logger.warning(f"Leak simulation {'activated' if active else 'deactivated'}")
    
    def reset(self):
        """إعادة ضبط الخزان"""
        self.water_level = self.config.initial_level
        self.water_volume = self._level_to_volume(self.water_level)
        self.temperature = 25.0
        self.pressure = 1.0
        self.ph_level = 7.0
        self.turbidity = 5.0
        self.is_filling = False
        self.is_draining = False
        self.leak_detected = False
    
    def get_state(self) -> Dict[str, Any]:
        """الحصول على حالة الخزان الحالية"""
        return {
            'water_level': round(self.water_level, 2),
            'water_volume': round(self.water_volume, 2),
            'temperature': round(self.temperature, 2),
            'pressure': round(self.pressure, 4),
            'ph_level': round(self.ph_level, 2),
            'turbidity': round(self.turbidity, 2),
            'is_filling': self.is_filling,
            'is_draining': self.is_draining,
            'leak_detected': self.leak_detected,
            'flow_rate': round(self.flow_rate, 2),
            'capacity': self.config.max_capacity,
            'last_update': self.last_update.isoformat()
        }
    
    def get_history(self, limit: int = 100) -> list:
        """الحصول على التاريخ"""
        return self.history[-limit:] if self.history else []