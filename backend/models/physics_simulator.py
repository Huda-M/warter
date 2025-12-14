import numpy as np
from typing import Dict, Any
from datetime import datetime, timedelta
import math

class PhysicsSimulator:
    """محاكاة الفيزياء المتقدمة للخزان"""
    
    def __init__(self):
        # ثوابت فيزيائية
        self.water_density = 997  # kg/m³ at 25°C
        self.gravity = 9.81  # m/s²
        self.specific_heat_water = 4182  # J/(kg·K)
        self.thermal_conductivity_steel = 50  # W/(m·K)
        
        # ظروف بيئية
        self.ambient_temperature = 20.0  # °C
        self.ambient_pressure = 101325  # Pa (1 atm)
        self.humidity = 0.5  # 50%
        
    def simulate_fluid_dynamics(self, tank_state: Dict[str, Any], dt: float) -> Dict[str, Any]:
        """محاكاة ديناميكية السوائل"""
        results = {}
        
        # حساب سرعة التدفق
        pipe_diameter = 0.05  # m (50mm pipe)
        flow_rate_lps = tank_state['flow_rate'] / 60  # لتر/ثانية
        flow_rate_m3s = flow_rate_lps / 1000
        
        if flow_rate_m3s > 0:
            cross_sectional_area = math.pi * (pipe_diameter/2)**2
            flow_velocity = flow_rate_m3s / cross_sectional_area
            results['flow_velocity'] = round(flow_velocity, 3)  # m/s
            
            # حساب رقم رينولدز
            kinematic_viscosity = 0.000001  # m²/s for water at 20°C
            reynolds_number = (flow_velocity * pipe_diameter) / kinematic_viscosity
            results['reynolds_number'] = round(reynolds_number, 0)
            
            # تحديد نمط التدفق
            if reynolds_number < 2000:
                results['flow_regime'] = 'laminar'
            elif reynolds_number > 4000:
                results['flow_regime'] = 'turbulent'
            else:
                results['flow_regime'] = 'transitional'
        
        # حساب القوى الهيدروستاتيكية
        tank_diameter = 1.5  # m
        tank_height = 2.0  # m
        water_height = (tank_state['water_volume'] / 1000) / (math.pi * (tank_diameter/2)**2)
        
        # قوة دفع الماء على جدران الخزان
        hydrostatic_force = 0.5 * self.water_density * self.gravity * water_height**2 * tank_diameter
        results['hydrostatic_force'] = round(hydrostatic_force, 2)  # N/m
        
        # عزم الانقلاب
        overturning_moment = hydrostatic_force * (water_height / 3)
        results['overturning_moment'] = round(overturning_moment, 2)  # N·m/m
        
        return results
    
    def simulate_heat_transfer(self, tank_state: Dict[str, Any], dt: float) -> Dict[str, Any]:
        """محاكاة انتقال الحرارة"""
        results = {}
        
        # معاملات الخزان
        tank_diameter = 1.5  # m
        tank_height = 2.0  # m
        insulation_thickness = 0.05  # m
        insulation_k = 0.04  # W/(m·K) for foam
        
        # مساحة سطح الخزان
        surface_area = math.pi * tank_diameter * tank_height + 2 * math.pi * (tank_diameter/2)**2
        
        # فرق درجة الحرارة
        delta_t = tank_state['temperature'] - self.ambient_temperature
        
        # حساب فقدان الحرارة عبر العزل
        if abs(delta_t) > 0.1:
            # مقاومة حرارية
            r_insulation = insulation_thickness / (insulation_k * surface_area)
            heat_loss = delta_t / r_insulation  # Watts
            
            # تغير درجة الحرارة مع الوقت
            water_mass = tank_state['water_volume']  # kg (1 liter ≈ 1 kg)
            temp_change = -heat_loss * dt / (water_mass * self.specific_heat_water)
            
            results['heat_loss_rate'] = round(heat_loss, 2)  # W
            results['temperature_change'] = round(temp_change, 4)  # °C/s
            results['time_constant'] = round(water_mass * self.specific_heat_water / (1/r_insulation), 0)  # s
        else:
            results['heat_loss_rate'] = 0
            results['temperature_change'] = 0
        
        # تأثير أشعة الشمس (إن وجد)
        solar_irradiance = 1000  # W/m² (شمس ساطعة)
        solar_absorption = 0.7  # معامل الامتصاص
        solar_gain = solar_irradiance * surface_area * solar_absorption * 0.5  # افتراض 50% تعرض
        
        results['solar_heat_gain'] = round(solar_gain, 2)
        results['net_heat_flow'] = round(solar_gain - results.get('heat_loss_rate', 0), 2)
        
        return results
    
    def simulate_water_quality(self, tank_state: Dict[str, Any], dt: float) -> Dict[str, Any]:
        """محاكاة جودة المياه"""
        results = {}
        
        # نمو بكتيري
        base_growth_rate = 0.01  # نمو/ساعة
        temperature_factor = max(0, (tank_state['temperature'] - 20) / 10)
        
        # نمو البكتيريا يزيد مع درجة الحرارة
        bacterial_growth = base_growth_rate * (1 + temperature_factor) * dt / 3600
        
        # تأثير مستوى الكلور (إن وجد)
        chlorine_level = 2.0  # ppm (مفترض)
        chlorine_decay = 0.1 * dt / 3600  # تحلل الكلور
        
        # تغير العكورة
        settling_rate = 0.05  # ترسب/ساعة
        turbidity_change = -settling_rate * dt / 3600
        
        # تغير الأس الهيدروجيني
        co2_absorption = 0.001  # امتصاص CO2
        ph_change = co2_absorption * np.random.uniform(-1, 1) * dt / 3600
        
        results['bacterial_growth'] = round(bacterial_growth, 6)
        results['chlorine_decay'] = round(chlorine_decay, 6)
        results['turbidity_change'] = round(turbidity_change, 6)
        results['ph_change'] = round(ph_change, 6)
        
        # مؤشر جودة المياه
        quality_score = 100
        quality_score -= tank_state['turbidity'] * 0.5
        quality_score -= abs(tank_state['ph_level'] - 7.0) * 10
        quality_score = max(0, min(100, quality_score))
        
        results['water_quality_score'] = round(quality_score, 1)
        results['quality_status'] = self._get_quality_status(quality_score)
        
        return results
    
    def _get_quality_status(self, score: float) -> str:
        """الحصول على حالة جودة المياه"""
        if score >= 90:
            return "ممتازة"
        elif score >= 75:
            return "جيدة"
        elif score >= 60:
            return "متوسطة"
        elif score >= 40:
            return "ضعيفة"
        else:
            return "غير صالحة"
    
    def simulate_structural_integrity(self, tank_state: Dict[str, Any]) -> Dict[str, Any]:
        """محاكاة السلامة الهيكلية للخزان"""
        results = {}
        
        # ضغوط المواد
        tank_diameter = 1.5  # m
        wall_thickness = 0.005  # m (5mm steel)
        yield_strength = 250e6  # Pa (250 MPa للصلب)
        
        # ضغط داخلي (ضغط الماء + ضغط الهواء)
        internal_pressure = tank_state['pressure'] * 100000  # Pa
        
        # ضغط دائري (hoop stress)
        hoop_stress = (internal_pressure * tank_diameter) / (2 * wall_thickness)
        
        # ضغط محوري (longitudinal stress)
        longitudinal_stress = (internal_pressure * tank_diameter) / (4 * wall_thickness)
        
        # عامل الأمان
        safety_factor_hoop = yield_strength / hoop_stress if hoop_stress > 0 else 999
        safety_factor_long = yield_strength / longitudinal_stress if longitudinal_stress > 0 else 999
        
        results['hoop_stress'] = round(hoop_stress / 1e6, 2)  # MPa
        results['longitudinal_stress'] = round(longitudinal_stress / 1e6, 2)  # MPa
        results['safety_factor_hoop'] = round(safety_factor_hoop, 2)
        results['safety_factor_long'] = round(safety_factor_long, 2)
        
        # حالة السلامة
        min_safety_factor = min(safety_factor_hoop, safety_factor_long)
        if min_safety_factor >= 3:
            results['structural_status'] = "آمن"
            results['integrity_score'] = 100
        elif min_safety_factor >= 2:
            results['structural_status'] = "مقبول"
            results['integrity_score'] = 75
        elif min_safety_factor >= 1.5:
            results['structural_status'] = "تحت المراقبة"
            results['integrity_score'] = 50
        else:
            results['structural_status'] = "خطر"
            results['integrity_score'] = 25
        
        # تأثير التعب (fatigue)
        # محاكاة تأثير دورات الملء والتفريغ
        cycles_per_day = 10  # تقديري
        fatigue_life = 10000  # دورة (تقديري)
        
        remaining_life = max(0, fatigue_life - cycles_per_day * 365)  # لمدة سنة
        results['estimated_fatigue_life'] = round(remaining_life / fatigue_life * 100, 1)  # نسبة
        
        return results
    
    def run_complete_simulation(self, tank_state: Dict[str, Any], dt: float = 1.0) -> Dict[str, Any]:
        """تشغيل محاكاة فيزيائية كاملة"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'fluid_dynamics': self.simulate_fluid_dynamics(tank_state, dt),
            'heat_transfer': self.simulate_heat_transfer(tank_state, dt),
            'water_quality': self.simulate_water_quality(tank_state, dt),
            'structural_integrity': self.simulate_structural_integrity(tank_state)
        }
        
        # حساب درجة المخاطر الإجمالية
        risk_factors = []
        
        # مخاطر ديناميكية السوائل
        fluid = results['fluid_dynamics']
        if fluid.get('reynolds_number', 0) > 4000:
            risk_factors.append(0.3)  # تدفق مضطرب
        
        # مخاطر انتقال الحرارة
        heat = results['heat_transfer']
        if abs(heat.get('net_heat_flow', 0)) > 1000:
            risk_factors.append(0.2)
        
        # مخاطر جودة المياه
        quality = results['water_quality']
        if quality.get('quality_status') in ["ضعيفة", "غير صالحة"]:
            risk_factors.append(0.4)
        
        # مخاطر هيكلية
        structure = results['structural_integrity']
        if structure.get('structural_status') in ["تحت المراقبة", "خطر"]:
            risk_factors.append(0.5)
        
        # درجة المخاطر الإجمالية
        if risk_factors:
            overall_risk = sum(risk_factors) / len(risk_factors)
        else:
            overall_risk = 0.1  # خطر منخفض
        
        results['overall_risk_score'] = round(overall_risk * 100, 1)
        results['risk_level'] = self._get_risk_level(overall_risk)
        
        return results
    
    def _get_risk_level(self, risk_score: float) -> str:
        """تحديد مستوى الخطر"""
        if risk_score >= 0.7:
            return "عالي جداً"
        elif risk_score >= 0.5:
            return "عالي"
        elif risk_score >= 0.3:
            return "متوسط"
        elif risk_score >= 0.1:
            return "منخفض"
        else:
            return "مقبول"