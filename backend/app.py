import os
import sys
import logging
from flask import Flask, jsonify, request  
from flask_cors import CORS
from flask_socketio import SocketIO
import gevent
from gevent import monkey
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
import time

# ⚠️ IMPORTANT: monkey.patch_all() يجب أن يكون قبل أي استيراد آخر
monkey.patch_all()

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إعداد Flask و SocketIO
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

# استيراد النماذج والأدوات
try:
    from models.tank_model import WaterTank
    from models.ai_decision import AIDecisionMaker
    from utils.data_logger import DataLogger
    from utils.alert_system import AlertSystem
    
    logger.info("✅ Models imported successfully")
except ImportError as e:
    logger.error(f"❌ Error importing models: {e}")
    sys.exit(1)

# إنشاء مثيلات عالمية
tank_model = WaterTank()
ai_system = AIDecisionMaker()
data_logger = DataLogger()
alert_system = AlertSystem(data_logger)

# حالة المحاكاة
simulation_running = False

# ==================== الصفحة الرئيسية ====================

@app.route('/')
def index():
    """الصفحة الرئيسية للـ API"""
    return jsonify({
        'name': 'Water Tank Digital Twin API',
        'version': '1.0.0',
        'status': 'running',
        'simulation_active': simulation_running,
        'features': [
            'Real-time monitoring',
            'AI-powered control',
            'Leak detection',
            'Consumption analysis',
            'Alert system',
            'WebSocket support'
        ],
        'endpoints': {
            'tank_state': '/api/tank/state',
            'tank_history': '/api/tank/history',
            'control_fill': '/api/control/fill',
            'control_drain': '/api/control/drain',
            'control_stop': '/api/control/stop',
            'alerts': '/api/alerts',
            'system_stats': '/api/system/stats',
            'consumption_analysis': '/api/analysis/consumption',
            'consumption_report': '/api/analysis/report',
            'simulation_start': '/api/simulation/start',
            'simulation_stop': '/api/simulation/stop'
        },
        'websocket': 'ws://localhost:5000'
    })

# ==================== Tank Endpoints ====================

@app.route('/api/tank/state', methods=['GET'])
def get_tank_state():
    """الحصول على حالة الخزان الحالية"""
    try:
        state = tank_model.get_state()
        return jsonify({
            'success': True,
            'data': state
        })
    except Exception as e:
        logger.error(f"Error getting tank state: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tank/history', methods=['GET'])
def get_tank_history():
    """الحصول على تاريخ قراءات الخزان"""
    try:
        limit = request.args.get('limit', default=100, type=int)
        history = tank_model.get_history(limit)
        return jsonify({
            'success': True,
            'data': history,
            'count': len(history)
        })
    except Exception as e:
        logger.error(f"Error getting tank history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tank/update', methods=['POST'])
def update_tank():
    """تحديث حالة الخزان (محاكاة مرور الوقت)"""
    try:
        data = request.json or {}
        dt = data.get('dt', 1.0)
        
        # تحديث الفيزياء
        tank_model.update_physics(dt)
        
        # تسجيل البيانات
        data_logger.log_tank_data(tank_model.get_state())
        
        return jsonify({
            'success': True,
            'state': tank_model.get_state()
        })
    except Exception as e:
        logger.error(f"Error updating tank: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== Control Endpoints ====================

@app.route('/api/control/fill', methods=['POST'])
def start_filling():
    """بدء عملية ملء الخزان"""
    try:
        tank_model.set_fill(True)
        data_logger.log_ai_message("💧 بدء الملء (يدوي)", "info")
        return jsonify({
            'success': True,
            'is_filling': True,
            'message': 'Filling started'
        })
    except Exception as e:
        logger.error(f"Error starting fill: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/control/drain', methods=['POST'])
def start_draining():
    """بدء عملية تفريغ الخزان"""
    try:
        tank_model.set_drain(True)
        data_logger.log_ai_message("📉 بدء التفريغ (يدوي)", "info")
        return jsonify({
            'success': True,
            'is_draining': True,
            'message': 'Draining started'
        })
    except Exception as e:
        logger.error(f"Error starting drain: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/control/stop', methods=['POST'])
def stop_all():
    """إيقاف جميع العمليات"""
    try:
        tank_model.set_fill(False)
        tank_model.set_drain(False)
        data_logger.log_ai_message("⏹ إيقاف العمليات", "info")
        return jsonify({
            'success': True,
            'is_filling': False,
            'is_draining': False,
            'message': 'All operations stopped'
        })
    except Exception as e:
        logger.error(f"Error stopping operations: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/control/flow_rate', methods=['POST'])
def set_flow_rate():
    """تعيين معدل التدفق"""
    try:
        data = request.json or {}
        rate = data.get('rate', 20)
        tank_model.set_flow_rate(rate)
        return jsonify({
            'success': True,
            'flow_rate': tank_model.flow_rate
        })
    except Exception as e:
        logger.error(f"Error setting flow rate: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/control/target', methods=['POST'])
def set_target_level():
    """تعيين مستوى الهدف"""
    try:
        data = request.json or {}
        target = data.get('target', 80)
        ai_system.config.target_level = target
        return jsonify({
            'success': True,
            'target_level': ai_system.config.target_level
        })
    except Exception as e:
        logger.error(f"Error setting target level: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/control/ai/decision', methods=['GET'])
def get_ai_decision():
    """الحصول على قرار الذكاء الاصطناعي"""
    try:
        state = tank_model.get_state()
        history = tank_model.get_history(20)
        action, message, details = ai_system.analyze(state, history)
        return jsonify({
            'success': True,
            'action': action.value,
            'message': message,
            'details': details
        })
    except Exception as e:
        logger.error(f"Error getting AI decision: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== Consumption Analysis ====================

@app.route('/api/analysis/consumption', methods=['GET'])
def get_consumption_analysis():
    """تحليل أنماط الاستهلاك"""
    try:
        from utils.consumption_analyzer import ConsumptionAnalyzer
        
        days = request.args.get('days', default=7, type=int)
        analyzer = ConsumptionAnalyzer()
        analysis = analyzer.analyze_consumption_patterns(days)
        
        return jsonify({
            'success': True,
            'data': analysis
        })
    except Exception as e:
        logger.error(f"Error analyzing consumption: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'تأكد من وجود بيانات كافية في قاعدة البيانات'
        }), 500

@app.route('/api/analysis/report', methods=['GET'])
def get_consumption_report():
    """توليد تقرير استهلاك نصي"""
    try:
        from utils.consumption_analyzer import ConsumptionAnalyzer
        from flask import Response
        
        days = request.args.get('days', default=7, type=int)
        analyzer = ConsumptionAnalyzer()
        report = analyzer.generate_report(days)
        
        return Response(
            report,
            mimetype='text/plain',
            headers={
                'Content-Disposition': f'attachment; filename=consumption_report_{days}d.txt'
            }
        )
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== System Stats ====================

@app.route('/api/system/stats', methods=['GET'])
def system_stats():
    """إحصائيات النظام"""
    try:
        # استخدام DataLogger للحصول على الإحصائيات
        import sqlite3
        from datetime import datetime, timedelta
        
        conn = sqlite3.connect(data_logger.db_path)
        cursor = conn.cursor()
        
        # عدد القراءات
        cursor.execute('SELECT COUNT(*) FROM tank_readings')
        total_readings = cursor.fetchone()[0]
        
        # آخر قراءة
        cursor.execute('SELECT timestamp FROM tank_readings ORDER BY timestamp DESC LIMIT 1')
        last_reading_row = cursor.fetchone()
        last_reading = last_reading_row[0] if last_reading_row else None
        
        # أول قراءة
        cursor.execute('SELECT timestamp FROM tank_readings ORDER BY timestamp ASC LIMIT 1')
        first_reading_row = cursor.fetchone()
        first_reading = first_reading_row[0] if first_reading_row else None
        
        # متوسط مستوى المياه في آخر 24 ساعة
        yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
        cursor.execute('''
            SELECT AVG(water_level) 
            FROM tank_readings 
            WHERE timestamp >= ?
        ''', (yesterday,))
        avg_level_row = cursor.fetchone()
        avg_water_level_24h = avg_level_row[0] if avg_level_row[0] else 0
        
        # التنبيهات النشطة
        cursor.execute('SELECT COUNT(*) FROM alerts WHERE resolved = FALSE')
        active_alerts = cursor.fetchone()[0]
        
        # سجلات الذكاء الاصطناعي
        cursor.execute('SELECT COUNT(*) FROM ai_logs')
        ai_logs_count = cursor.fetchone()[0]
        
        conn.close()
        
        stats = {
            'tank_readings_count': total_readings,
            'first_reading': first_reading,
            'last_reading': last_reading,
            'active_alerts': active_alerts,
            'ai_logs_count': ai_logs_count,
            'avg_water_level_24h': round(avg_water_level_24h, 2) if avg_water_level_24h else 0,
            'simulation_running': simulation_running,
            'current_state': tank_model.get_state()
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== Alerts ====================

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """الحصول على التنبيهات"""
    try:
        unresolved_only = request.args.get('unresolved_only', 'true').lower() == 'true'
        limit = request.args.get('limit', default=100, type=int)
        severity = request.args.get('severity', type=str)
        
        alerts = data_logger.get_alerts(unresolved_only, limit, severity)
        return jsonify({
            'success': True,
            'data': alerts,
            'count': len(alerts)
        })
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/alerts/<int:alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """التعرف على تنبيه"""
    try:
        alert_system.acknowledge_alert(alert_id)
        return jsonify({
            'success': True,
            'message': f'Alert {alert_id} acknowledged'
        })
    except Exception as e:
        logger.error(f"Error acknowledging alert {alert_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/alerts/clear', methods=['POST'])
def clear_alerts():
    """حذف جميع التنبيهات"""
    try:
        import sqlite3
        conn = sqlite3.connect(data_logger.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE alerts SET resolved = TRUE')
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'All alerts cleared'
        })
    except Exception as e:
        logger.error(f"Error clearing alerts: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== Simulation ====================

@app.route('/api/simulation/start', methods=['POST'])
def start_simulation():
    """بدء المحاكاة"""
    global simulation_running
    
    if not simulation_running:
        simulation_running = True
        
        # بدء حلقة المحاكاة في thread منفصل
        import threading
        thread = threading.Thread(target=tank_simulation_loop, daemon=True)
        thread.start()
        
        data_logger.log_ai_message("🚀 بدء محاكاة التوأم الرقمي", "system")
        logger.info("✅ Simulation started")
        
        return jsonify({
            'success': True,
            'message': 'Simulation started successfully'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Simulation is already running'
        }), 400

@app.route('/api/simulation/stop', methods=['POST'])
def stop_simulation():
    """إيقاف المحاكاة"""
    global simulation_running
    
    simulation_running = False
    data_logger.log_ai_message("⏹ إيقاف محاكاة التوأم الرقمي", "system")
    logger.info("⏹ Simulation stopped")
    
    return jsonify({
        'success': True,
        'message': 'Simulation stopped successfully'
    })

@app.route('/api/simulation/status', methods=['GET'])
def simulation_status():
    """حالة المحاكاة"""
    return jsonify({
        'success': True,
        'data': {
            'running': simulation_running,
            'tank_state': tank_model.get_state(),
            'ai_mode': tank_model.ai_mode
        }
    })

# ==================== محاكاة الخزان ====================

def tank_simulation_loop():
    """حلقة محاكاة الخزان في الوقت الحقيقي"""
    global simulation_running
    
    logger.info("🚀 Simulation loop started")
    
    while simulation_running:
        try:
            # تحديث الفيزياء
            tank_model.update_physics(dt=1.0)
            
            # تسجيل البيانات
            current_state = tank_model.get_state()
            data_logger.log_tank_data(current_state)
            
            # كشف التنبيهات
            alerts = alert_system.check_alerts(current_state)
            if alerts:
                for alert in alerts:
                    socketio.emit('alert', alert)
                    logger.warning(f"🚨 Alert: {alert.get('message', 'Unknown')}")
            
            # إرسال تحديث عبر WebSocket
            socketio.emit('tank_update', current_state)
            
            # قرارات الذكاء الاصطناعي
            if tank_model.ai_mode:
                history = data_logger.get_tank_data(limit=20)
                action, message, details = ai_system.analyze(current_state, history)
                
                # تنفيذ القرار
                if action.value == "fill":
                    tank_model.set_fill(True)
                    tank_model.set_drain(False)
                elif action.value == "drain":
                    tank_model.set_fill(False)
                    tank_model.set_drain(True)
                elif action.value == "stop":
                    tank_model.set_fill(False)
                    tank_model.set_drain(False)
                
                if message:
                    data_logger.log_ai_message(message, 'ai_decision', details)
                    socketio.emit('ai_log', {
                        'message': message,
                        'type': 'ai_decision',
                        'details': details,
                        'timestamp': time.time()
                    })
            
            # انتظار ثانية واحدة
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"❌ Error in simulation loop: {e}")
            time.sleep(1)
    
    logger.info("⏹ Simulation loop stopped")

# ==================== WebSocket Events ====================

@socketio.on('connect')
def handle_connect():
    """عند اتصال عميل جديد"""
    logger.info('🔌 Client connected')
    socketio.emit('connected', {
        'message': 'Connected to Water Tank Digital Twin',
        'timestamp': time.time(),
        'simulation_running': simulation_running
    })
    
    # إرسال الحالة الأولية
    state = tank_model.get_state()
    socketio.emit('tank_update', state)

@socketio.on('disconnect')
def handle_disconnect():
    """عند قطع اتصال عميل"""
    logger.info('🔌 Client disconnected')

@socketio.on('request_update')
def handle_request_update(data):
    """طلب تحديث البيانات"""
    component = data.get('component', 'tank')
    
    try:
        if component == 'tank':
            state = tank_model.get_state()
            socketio.emit('tank_update', state)
        
        elif component == 'alerts':
            alerts = data_logger.get_alerts(unresolved_only=True, limit=10)
            socketio.emit('alerts_update', alerts)
        
        elif component == 'ai_logs':
            logs = ai_system.get_recent_logs(10)
            socketio.emit('ai_logs_update', logs)
        
        elif component == 'all':
            # إرسال كل البيانات
            socketio.emit('tank_update', tank_model.get_state())
            socketio.emit('alerts_update', data_logger.get_alerts(unresolved_only=True, limit=10))
            socketio.emit('ai_logs_update', ai_system.get_recent_logs(10))
            
    except Exception as e:
        logger.error(f"Error handling request_update: {e}")
        socketio.emit('error', {'message': str(e)})

# ==================== معالج الأخطاء ====================

@app.errorhandler(404)
def not_found(error):
    """معالج 404"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': str(error),
        'available_endpoints': {
            'home': '/',
            'tank_state': '/api/tank/state',
            'tank_history': '/api/tank/history',
            'control_fill': '/api/control/fill',
            'alerts': '/api/alerts',
            'consumption_analysis': '/api/analysis/consumption',
            'system_stats': '/api/system/stats'
        }
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """معالج 500"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': str(error)
    }), 500

# ==================== بدء التشغيل ====================

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🌊 Water Tank Digital Twin System")
    logger.info("=" * 60)
    logger.info("📡 API URL: http://0.0.0.0:5000")
    logger.info("🔌 WebSocket URL: ws://0.0.0.0:5000")
    logger.info("=" * 60)
    
    # بدء المحاكاة تلقائياً
    simulation_running = True
    import threading
    sim_thread = threading.Thread(target=tank_simulation_loop, daemon=True)
    sim_thread.start()
    logger.info("✅ Auto-started simulation thread")
    
    # تشغيل الخادم
    try:
        server = WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler)
        logger.info("🚀 Server is running on http://0.0.0.0:5000")
        logger.info("=" * 60)
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down server...")
        simulation_running = False
        logger.info("✅ Server stopped successfully")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        simulation_running = False