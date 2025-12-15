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

# استيراد Blueprints
try:
    from api.tank_api import tank_bp
    from api.control_api import control_bp
    from api.simulation_api import simulation_bp
    
    app.register_blueprint(tank_bp, url_prefix='/api')
    app.register_blueprint(control_bp, url_prefix='/api')
    app.register_blueprint(simulation_bp, url_prefix='/api')
    
    logger.info("✅ Blueprints registered successfully")
except ImportError as e:
    logger.error(f"❌ Error importing Blueprints: {e}")
    sys.exit(1)

# استيراد محلل الاستهلاك
try:
    from utils.consumption_analyzer import ConsumptionAnalyzer, create_consumption_endpoint
    logger.info("✅ Consumption Analyzer imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Consumption Analyzer not found: {e}")
    ConsumptionAnalyzer = None
    create_consumption_endpoint = None

# إنشاء مثيلات عالمية
tank_model = WaterTank()
ai_system = AIDecisionMaker()
data_logger = DataLogger()
alert_system = AlertSystem(data_logger)

# إنشاء محلل الاستهلاك إذا كان متاحاً
if ConsumptionAnalyzer:
    consumption_analyzer = ConsumptionAnalyzer()
    create_consumption_endpoint(app, consumption_analyzer)
    logger.info("✅ Consumption analysis endpoints registered")

# حالة المحاكاة
simulation_running = False

@app.route('/')
def index():
    """الصفحة الرئيسية للـ API"""
    endpoints = {
        'tank': '/api/tank/state',
        'control': '/api/control/fill',
        'simulation': '/api/simulation/scenarios',
        'alerts': '/api/alerts',
        'system_stats': '/api/system/stats'
    }
    
    # إضافة endpoints التحليل إذا كانت متاحة
    if ConsumptionAnalyzer:
        endpoints['consumption_analysis'] = '/api/analysis/consumption'
        endpoints['consumption_report'] = '/api/analysis/report'
    
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
        'endpoints': endpoints,
        'websocket': 'ws://localhost:5000'
    })

@app.route('/api/system/stats', methods=['GET'])
def system_stats():
    """إحصائيات النظام"""
    try:
        stats = data_logger.get_system_stats()
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
            'data': alerts
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
        success = alert_system.acknowledge_alert(alert_id)
        if success:
            return jsonify({
                'success': True,
                'message': f'Alert {alert_id} acknowledged'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Alert {alert_id} not found'
            }), 404
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
        alert_system.clear_all_alerts()
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

# ==================== WebSocket Events ====================

@socketio.on('connect')
def handle_connect():
    """عند اتصال عميل جديد"""
    logger.info('🔌 Client connected')
    socketio.emit('connected', {
        'message': 'Connected to Water Tank Digital Twin',
        'timestamp': gevent.time.time(),
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

@socketio.on('subscribe')
def handle_subscribe(data):
    """الاشتراك في قناة"""
    channel = data.get('channel')
    logger.info(f'📡 Client subscribed to {channel}')
    socketio.emit('subscribed', {'channel': channel, 'success': True})

@socketio.on('control_command')
def handle_control_command(data):
    """معالجة أوامر التحكم"""
    command = data.get('command')
    params = data.get('params', {})
    
    logger.info(f'🎮 Control command: {command} with params {params}')
    
    try:
        # تنفيذ الأمر
        if command == 'fill':
            tank_model.set_fill(True)
            data_logger.log_ai_message("💧 بدء الملء (عن طريق WebSocket)", "info")
            
        elif command == 'drain':
            tank_model.set_drain(True)
            data_logger.log_ai_message("📉 بدء التفريغ (عن طريق WebSocket)", "info")
            
        elif command == 'stop':
            tank_model.set_fill(False)
            tank_model.set_drain(False)
            data_logger.log_ai_message("⏹ إيقاف العمليات (عن طريق WebSocket)", "info")
        
        elif command == 'set_target':
            target = params.get('target', 80)
            ai_system.config.target_level = target
            data_logger.log_ai_message(f"🎯 تغيير المستوى المستهدف إلى {target}%", "info")
        
        elif command == 'toggle_ai':
            tank_model.ai_mode = not tank_model.ai_mode
            mode = "آلي" if tank_model.ai_mode else "يدوي"
            data_logger.log_ai_message(f"🔄 تبديل إلى الوضع {mode}", "info")
        
        # إرسال التحديث
        state = tank_model.get_state()
        socketio.emit('tank_update', state)
        socketio.emit('command_executed', {
            'command': command,
            'success': True,
            'state': state
        })
        
    except Exception as e:
        logger.error(f"Error executing command {command}: {e}")
        socketio.emit('command_executed', {
            'command': command,
            'success': False,
            'error': str(e)
        })

# ==================== محاكاة الخزان ====================

def tank_simulation_loop():
    """حلقة محاكاة الخزان في الوقت الحقيقي"""
    import time
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

# ==================== معالج الأخطاء ====================

@app.errorhandler(404)
def not_found(error):
    """معالج 404"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': str(error)
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