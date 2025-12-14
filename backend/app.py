import os
import sys
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import eventlet

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إعداد Flask و SocketIO
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# استيراد Blueprints من api
try:
    from api.tank_api import tank_bp
    from api.control_api import control_bp
    from api.simulation_api import simulation_bp
    app.register_blueprint(tank_bp)
    app.register_blueprint(control_bp)
    app.register_blueprint(simulation_bp)
except ImportError as e:
    logger.error(f"Error importing Blueprints: {e}")
    sys.exit(1)

# استيراد النماذج
from models.tank_model import WaterTank
from models.ai_decision import AIDecisionMaker
from utils.data_logger import DataLogger
from utils.alert_system import AlertSystem

# إنشاء مثيلات عالمية
tank_model = WaterTank()
ai_system = AIDecisionMaker()
data_logger = DataLogger()
alert_system = AlertSystem(data_logger)

# حالة المحاكاة
simulation_running = False

@app.route('/')
def index():
    """الصفحة الرئيسية للـ API"""
    return jsonify({
        'name': 'Water Tank Digital Twin API',
        'version': '1.0.0',
        'endpoints': {
            'tank': '/api/tank/state',
            'control': '/api/control/mode',
            'simulation': '/api/simulation/scenarios',
            'alerts': '/api/alerts'
        },
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

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    socketio.emit('connected', {'message': 'Connected to Water Tank Digital Twin'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on('request_update')
def handle_request_update(data):
    """طلب تحديث البيانات"""
    component = data.get('component', 'tank')
    if component == 'tank':
        state = tank_model.get_state()
        socketio.emit('tank_update', state)
    elif component == 'alerts':
        alerts = data_logger.get_alerts(unresolved_only=True, limit=10)
        socketio.emit('alerts_update', alerts)
    elif component == 'ai_logs':
        logs = ai_system.get_recent_logs(10)
        socketio.emit('ai_logs_update', logs)

@socketio.on('subscribe')
def handle_subscribe(data):
    """الاشتراك في قناة"""
    channel = data.get('channel')
    logger.info(f'Client subscribed to {channel}')
    # يمكن تنفيذ منطق الاشتراك هنا

@socketio.on('control_command')
def handle_control_command(data):
    """معالجة أوامر التحكم"""
    command = data.get('command')
    params = data.get('params', {})
    
    logger.info(f'Control command: {command} with params {params}')
    
    # تنفيذ الأمر
    # هذا مثال مبسط - يمكن تفصيله أكثر
    if command == 'fill':
        tank_model.set_fill(True)
    elif command == 'drain':
        tank_model.set_drain(True)
    elif command == 'stop':
        tank_model.set_fill(False)
        tank_model.set_drain(False)
    
    # إرسال التحديث
    state = tank_model.get_state()
    socketio.emit('tank_update', state)

# محاكاة الخزان في الوقت الحقيقي
def tank_simulation_loop():
    """حلقة محاكاة الخزان"""
    import time
    global simulation_running
    
    while simulation_running:
        try:
            # تحديث الفيزياء
            tank_model.update_physics(dt=1.0)
            
            # تسجيل البيانات
            data_logger.log_tank_data(tank_model.get_state())
            
            # كشف التنبيهات
            alerts = alert_system.check_alerts(tank_model.get_state())
            for alert in alerts:
                socketio.emit('alert', alert)
            
            # إرسال تحديث عبر WebSocket
            socketio.emit('tank_update', tank_model.get_state())
            
            # قرارات الذكاء الاصطناعي
            if tank_model.ai_mode:  # نفترض وجود هذا الحقل
                history = data_logger.get_tank_data(limit=20)
                action, message, details = ai_system.analyze(tank_model.get_state(), history)
                if message:
                    data_logger.log_ai_message(message, 'ai_decision', details)
                    socketio.emit('ai_log', {
                        'message': message,
                        'type': 'ai_decision',
                        'timestamp': time.time()
                    })
            
            time.sleep(1)  # تحديث كل ثانية
            
        except Exception as e:
            logger.error(f"Error in simulation loop: {e}")
            time.sleep(1)

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
        
        return jsonify({
            'success': True,
            'message': 'Simulation started'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Simulation already running'
        })

@app.route('/api/simulation/stop', methods=['POST'])
def stop_simulation():
    """إيقاف المحاكاة"""
    global simulation_running
    simulation_running = False
    
    data_logger.log_ai_message("⏹ إيقاف محاكاة التوأم الرقمي", "system")
    
    return jsonify({
        'success': True,
        'message': 'Simulation stopped'
    })

if __name__ == '__main__':
    logger.info("Starting Water Tank Digital Twin Server...")
    logger.info("API URL: http://localhost:5000")
    logger.info("WebSocket URL: ws://localhost:5000")
    
    # بدء المحاكاة تلقائياً
    simulation_running = True
    import threading
    sim_thread = threading.Thread(target=tank_simulation_loop, daemon=True)
    sim_thread.start()
    
    # تشغيل الخادم
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)