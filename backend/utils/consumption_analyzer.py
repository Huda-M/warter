# backend/utils/consumption_analyzer.py
"""
نظام تحليل أنماط استهلاك المياه - يكمل متطلبات المشروع
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sqlite3
from pathlib import Path

class ConsumptionAnalyzer:
    """محلل أنماط استهلاك المياه"""
    
    def __init__(self, db_path="data/historical_data.db"):
        self.db_path = Path(db_path)
        
    def analyze_consumption_patterns(self, days=7) -> Dict[str, Any]:
        """تحليل أنماط الاستهلاك"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جلب البيانات التاريخية
        start_date = datetime.now() - timedelta(days=days)
        cursor.execute('''
            SELECT timestamp, water_level, water_volume, is_filling, is_draining
            FROM tank_readings
            WHERE timestamp >= ?
            ORDER BY timestamp ASC
        ''', (start_date.isoformat(),))
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            return {
                "status": "insufficient_data",
                "message": "لا توجد بيانات كافية للتحليل"
            }
        
        # تحليل الأنماط
        analysis = {
            "period": f"{days} أيام",
            "total_readings": len(data),
            "consumption_rate": self._calculate_consumption_rate(data),
            "peak_usage_times": self._find_peak_times(data),
            "daily_patterns": self._analyze_daily_patterns(data),
            "efficiency_score": self._calculate_efficiency(data),
            "predictions": self._predict_future_usage(data),
            "recommendations": []
        }
        
        # إضافة توصيات
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _calculate_consumption_rate(self, data: List) -> Dict[str, float]:
        """حساب معدل الاستهلاك"""
        if len(data) < 2:
            return {"average": 0, "min": 0, "max": 0}
        
        consumption_rates = []
        for i in range(1, len(data)):
            time_diff = (datetime.fromisoformat(data[i][0]) - 
                        datetime.fromisoformat(data[i-1][0])).total_seconds() / 3600
            
            if time_diff > 0:
                volume_diff = data[i-1][2] - data[i][2]  # water_volume
                rate = volume_diff / time_diff  # لتر/ساعة
                
                if rate > 0:  # استهلاك فقط
                    consumption_rates.append(rate)
        
        if not consumption_rates:
            return {"average": 0, "min": 0, "max": 0}
        
        return {
            "average": round(np.mean(consumption_rates), 2),
            "min": round(np.min(consumption_rates), 2),
            "max": round(np.max(consumption_rates), 2),
            "unit": "لتر/ساعة"
        }
    
    def _find_peak_times(self, data: List) -> List[Dict]:
        """تحديد أوقات الذروة للاستهلاك"""
        hourly_consumption = {}
        
        for i in range(1, len(data)):
            timestamp = datetime.fromisoformat(data[i][0])
            hour = timestamp.hour
            
            volume_diff = data[i-1][2] - data[i][2]
            if volume_diff > 0:
                hourly_consumption[hour] = hourly_consumption.get(hour, 0) + volume_diff
        
        # ترتيب الساعات حسب الاستهلاك
        sorted_hours = sorted(hourly_consumption.items(), 
                            key=lambda x: x[1], reverse=True)
        
        peak_times = []
        for hour, consumption in sorted_hours[:3]:
            peak_times.append({
                "hour": f"{hour:02d}:00",
                "consumption": round(consumption, 2),
                "period": self._get_period_name(hour)
            })
        
        return peak_times
    
    def _get_period_name(self, hour: int) -> str:
        """تحديد فترة اليوم"""
        if 6 <= hour < 12:
            return "صباحاً"
        elif 12 <= hour < 17:
            return "ظهراً"
        elif 17 <= hour < 21:
            return "مساءً"
        else:
            return "ليلاً"
    
    def _analyze_daily_patterns(self, data: List) -> Dict[str, Any]:
        """تحليل الأنماط اليومية"""
        daily_data = {}
        
        for entry in data:
            timestamp = datetime.fromisoformat(entry[0])
            date = timestamp.date()
            
            if date not in daily_data:
                daily_data[date] = {
                    "levels": [],
                    "fills": 0,
                    "drains": 0
                }
            
            daily_data[date]["levels"].append(entry[1])  # water_level
            if entry[3]:  # is_filling
                daily_data[date]["fills"] += 1
            if entry[4]:  # is_draining
                daily_data[date]["drains"] += 1
        
        # حساب الإحصائيات اليومية
        patterns = {
            "avg_fills_per_day": round(np.mean([d["fills"] for d in daily_data.values()]), 1),
            "avg_drains_per_day": round(np.mean([d["drains"] for d in daily_data.values()]), 1),
            "most_stable_day": None,
            "most_volatile_day": None
        }
        
        # تحديد أكثر الأيام استقراراً
        stabilities = {}
        for date, info in daily_data.items():
            if len(info["levels"]) > 1:
                std = np.std(info["levels"])
                stabilities[date] = std
        
        if stabilities:
            patterns["most_stable_day"] = str(min(stabilities, key=stabilities.get))
            patterns["most_volatile_day"] = str(max(stabilities, key=stabilities.get))
        
        return patterns
    
    def _calculate_efficiency(self, data: List) -> Dict[str, Any]:
        """حساب كفاءة النظام"""
        total_fills = sum(1 for entry in data if entry[3])  # is_filling
        total_drains = sum(1 for entry in data if entry[4])  # is_draining
        
        # حساب الوقت المستغرق في الملء/التفريغ
        fill_time = 0
        drain_time = 0
        
        for i in range(1, len(data)):
            time_diff = (datetime.fromisoformat(data[i][0]) - 
                        datetime.fromisoformat(data[i-1][0])).total_seconds()
            
            if data[i][3]:  # is_filling
                fill_time += time_diff
            if data[i][4]:  # is_draining
                drain_time += time_diff
        
        total_time = (datetime.fromisoformat(data[-1][0]) - 
                     datetime.fromisoformat(data[0][0])).total_seconds()
        
        idle_time = total_time - fill_time - drain_time
        
        # حساب درجة الكفاءة (0-100)
        efficiency_score = 100
        
        # خصم نقاط للملء/التفريغ المتكرر
        if total_fills > 50:
            efficiency_score -= min(20, (total_fills - 50) * 0.5)
        
        # خصم نقاط للوقت الخامل الطويل
        idle_percentage = (idle_time / total_time) * 100
        if idle_percentage > 80:
            efficiency_score -= 10
        
        efficiency_score = max(0, min(100, efficiency_score))
        
        return {
            "score": round(efficiency_score, 1),
            "total_fills": total_fills,
            "total_drains": total_drains,
            "idle_percentage": round(idle_percentage, 1),
            "fill_time_hours": round(fill_time / 3600, 1),
            "drain_time_hours": round(drain_time / 3600, 1),
            "rating": self._get_efficiency_rating(efficiency_score)
        }
    
    def _get_efficiency_rating(self, score: float) -> str:
        """تحديد تقييم الكفاءة"""
        if score >= 90:
            return "ممتاز"
        elif score >= 75:
            return "جيد جداً"
        elif score >= 60:
            return "جيد"
        elif score >= 40:
            return "متوسط"
        else:
            return "ضعيف"
    
    def _predict_future_usage(self, data: List) -> Dict[str, Any]:
        """التنبؤ بالاستخدام المستقبلي"""
        if len(data) < 10:
            return {"status": "insufficient_data"}
        
        # استخراج البيانات
        levels = [entry[1] for entry in data[-50:]]  # آخر 50 قراءة
        
        # حساب الاتجاه
        x = np.arange(len(levels))
        coeffs = np.polyfit(x, levels, 1)
        trend = coeffs[0]  # الميل
        
        # التنبؤ للساعات القادمة
        predictions = []
        current_level = levels[-1]
        
        for hour in range(1, 25):
            predicted_level = current_level + (trend * hour * 10)
            predicted_level = max(0, min(100, predicted_level))
            
            predictions.append({
                "hour": hour,
                "predicted_level": round(predicted_level, 1),
                "confidence": self._calculate_confidence(hour, len(data))
            })
        
        return {
            "trend": "تنازلي" if trend < -0.1 else "تصاعدي" if trend > 0.1 else "مستقر",
            "trend_rate": round(trend, 3),
            "predictions_24h": predictions[:24],
            "estimated_refill_time": self._estimate_refill_time(predictions, 20)
        }
    
    def _calculate_confidence(self, hour: int, data_points: int) -> str:
        """حساب مستوى الثقة في التنبؤ"""
        base_confidence = min(100, (data_points / 100) * 100)
        time_penalty = hour * 2
        
        confidence = base_confidence - time_penalty
        
        if confidence >= 80:
            return "عالية"
        elif confidence >= 60:
            return "متوسطة"
        else:
            return "منخفضة"
    
    def _estimate_refill_time(self, predictions: List, threshold: float) -> Dict[str, Any]:
        """تقدير وقت إعادة الملء"""
        for pred in predictions:
            if pred["predicted_level"] <= threshold:
                return {
                    "hours": pred["hour"],
                    "at_level": pred["predicted_level"],
                    "action_required": True
                }
        
        return {
            "hours": None,
            "at_level": None,
            "action_required": False,
            "message": "لا حاجة لإعادة الملء خلال 24 ساعة"
        }
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """توليد توصيات بناءً على التحليل"""
        recommendations = []
        
        # توصيات الكفاءة
        efficiency = analysis.get("efficiency_score", {})
        if efficiency.get("score", 100) < 60:
            recommendations.append(
                "⚠️ كفاءة النظام منخفضة - يُنصح بمراجعة إعدادات التحكم"
            )
        
        if efficiency.get("total_fills", 0) > 50:
            recommendations.append(
                "🔄 عدد مرات الملء مرتفع - قد يكون هناك تسرب أو استهلاك غير طبيعي"
            )
        
        # توصيات أوقات الذروة
        peak_times = analysis.get("peak_usage_times", [])
        if peak_times:
            top_hour = peak_times[0]["hour"]
            recommendations.append(
                f"📊 أعلى استهلاك في الساعة {top_hour} - خطط للتعبئة قبلها"
            )
        
        # توصيات التنبؤ
        predictions = analysis.get("predictions", {})
        refill_time = predictions.get("estimated_refill_time", {})
        if refill_time.get("action_required"):
            hours = refill_time["hours"]
            recommendations.append(
                f"⏰ يُتوقع الحاجة لإعادة الملء خلال {hours} ساعة"
            )
        
        # توصيات الاستقرار
        daily = analysis.get("daily_patterns", {})
        if daily.get("most_volatile_day"):
            recommendations.append(
                f"📉 اليوم الأكثر تقلباً: {daily['most_volatile_day']}"
            )
        
        if not recommendations:
            recommendations.append("✅ النظام يعمل بكفاءة عالية - لا توجد توصيات حالياً")
        
        return recommendations
    
    def generate_report(self, days=7) -> str:
        """توليد تقرير شامل"""
        analysis = self.analyze_consumption_patterns(days)
        
        report = f"""
╔═══════════════════════════════════════════════════════════╗
║          تقرير تحليل استهلاك المياه - {days} أيام            ║
╚═══════════════════════════════════════════════════════════╝

📊 معدل الاستهلاك:
   • المتوسط: {analysis['consumption_rate']['average']} لتر/ساعة
   • الأدنى: {analysis['consumption_rate']['min']} لتر/ساعة
   • الأقصى: {analysis['consumption_rate']['max']} لتر/ساعة

⏰ أوقات الذروة:
"""
        for peak in analysis.get('peak_usage_times', []):
            report += f"   • {peak['hour']} ({peak['period']}): {peak['consumption']} لتر\n"
        
        report += f"""
📈 الأنماط اليومية:
   • متوسط مرات الملء: {analysis['daily_patterns']['avg_fills_per_day']}/يوم
   • متوسط مرات التفريغ: {analysis['daily_patterns']['avg_drains_per_day']}/يوم
   • اليوم الأكثر استقراراً: {analysis['daily_patterns']['most_stable_day']}
   • اليوم الأكثر تقلباً: {analysis['daily_patterns']['most_volatile_day']}

⚡ كفاءة النظام:
   • الدرجة: {analysis['efficiency_score']['score']}/100 ({analysis['efficiency_score']['rating']})
   • إجمالي الملء: {analysis['efficiency_score']['total_fills']}
   • إجمالي التفريغ: {analysis['efficiency_score']['total_drains']}
   • نسبة الخمول: {analysis['efficiency_score']['idle_percentage']}%

🔮 التنبؤات:
   • الاتجاه: {analysis['predictions']['trend']}
   • معدل التغير: {analysis['predictions']['trend_rate']}%/ساعة
"""
        
        refill = analysis['predictions'].get('estimated_refill_time', {})
        if refill.get('action_required'):
            report += f"   • الحاجة لإعادة الملء: خلال {refill['hours']} ساعة\n"
        else:
            report += f"   • {refill.get('message', 'لا حاجة لإعادة الملء')}\n"
        
        report += "\n💡 التوصيات:\n"
        for rec in analysis.get('recommendations', []):
            report += f"   {rec}\n"
        
        report += "\n" + "═" * 59 + "\n"
        
        return report


# API endpoint للاستخدام
def create_consumption_endpoint(app, analyzer):
    """إنشاء endpoint للتحليل"""
    
    @app.route('/api/analysis/consumption', methods=['GET'])
    def get_consumption_analysis():
        from flask import jsonify, request
        
        days = request.args.get('days', default=7, type=int)
        analysis = analyzer.analyze_consumption_patterns(days)
        
        return jsonify({
            'success': True,
            'data': analysis
        })
    
    @app.route('/api/analysis/report', methods=['GET'])
    def get_consumption_report():
        from flask import Response, request
        
        days = request.args.get('days', default=7, type=int)
        report = analyzer.generate_report(days)
        
        return Response(
            report,
            mimetype='text/plain',
            headers={
                'Content-Disposition': f'attachment; filename=consumption_report_{days}d.txt'
            }
        )


# مثال للاستخدام
if __name__ == "__main__":
    analyzer = ConsumptionAnalyzer()
    
    # تحليل الاستهلاك
    analysis = analyzer.analyze_consumption_patterns(days=7)
    print(analysis)
    
    # توليد تقرير
    report = analyzer.generate_report(days=7)
    print(report)