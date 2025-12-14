from flask_socketio import SocketIO, emit
from ..models.tank_model import WaterTank
from ..models.ai_decision import AIDecisionMaker
from .data_logger import DataLogger
from .alert_system import AlertSystem
import threading
import time
from datetime import datetime

class WebSocketManager:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.tank = WaterTank()
        self.ai = AIDecisionMaker()
        self.data_logger = DataLogger()
        self.alert_system = AlertSystem(self.data_logger)
        
        self.simulation_running = False
        self.simulation_thread = None
        
        self.setup_handlers()
    
    def setup_handlers(self):
        """إعداد معالجات WebSocket"""
        
        @self.socketio.on('connect')
        def handle_connect():
            print('Client connected')
            emit('connected', {'message': 'Connected to Digital Twin'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print('Client disconnected')
        
        @self.socketio.on('get_tank_state')
        def handle_get_state():
            state = self.tank.get_state()
            emit('tank_state', state)
        
        @self.socketio.on('start_fill')
        def handle_start_fill():
            self.tank.set_fill(True)
            emit('operation_started', {'operation': 'fill'})
        
        @self.socketio.on('start_drain')
        def handle_start_drain():
            self.tank.set_drain(True)
            emit('operation_started', {'operation': 'drain'})
        
        @self.socketio.on('stop_operations')
        def handle_stop():
            self.tank.set_fill(False)
            self.tank.set_drain(False)
            emit('operations_stopped', {})
        
        @self.socketio.on('set_flow_rate')
        def handle_set_flow_rate(data):
            rate = data.get('rate', 20)
            self.tank.set_flow_rate(rate)
            emit('flow_rate_updated', {'rate': rate})
        
        @self.socketio.on('set_target_level')
        def handle_set_target(data):
            target = data.get('target', 80)
            self.ai.config.target_level = target
            emit('target_updated', {'target': target})
        
        @self.socketio.on('toggle_simulation')
        def handle_toggle_simulation(data):
            run = data.get('run', False)
            if run and not self.simulation_running:
                self.start_simulation()
            elif not run and self.simulation_running:
                self.stop_simulation()
            
            emit('simulation_toggled', {'running': self.simulation_running})
    
    def start_simulation(self):
        """بدء محاكاة الوقت الحقيقي"""
        if self.simulation_running:
            return
        
        self.simulation_running = True
        self.simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self.simulation_thread.start()
    
    def stop_simulation(self):
        """إيقاف المحاكاة"""
        self.simulation_running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=2)
    
    def _simulation_loop(self):
        """حلقة المحاكاة الرئيسية"""
        update_interval = 1.0  # تحديث كل ثانية
        
        while self.simulation_running:
            try:
                # تحديث الفيزياء
                state = self.tank.update_physics(update_interval)
                
                # تسجيل البيانات
                self.data_logger.log_tank_data(state)
                
                # التحقق من التنبيهات
                alerts = self.alert_system.check_alerts(state)
                
                # اتخاذ قرار الذكاء الاصطناعي
                history = self.tank.get_history(20)
                action, message, details = self.ai.analyze(state, history)
                
                # تنفيذ قرار الذكاء الاصطناعي
                if action.value == "fill":
                    self.tank.set_fill(True)
                    self.tank.set_drain(False)
                elif action.value == "drain":
                    self.tank.set_fill(False)
                    self.tank.set_drain(True)
                elif action.value == "stop":
                    self.tank.set_fill(False)
                    self.tank.set_drain(False)
                
                # تسجيل قرار الذكاء الاصطناعي
                if message:
                    self.data_logger.log_ai_message(message, "ai_decision")
                
                # إرسال تحديثات عبر WebSocket
                self.socketio.emit('tank_update', {
                    'state': state,
                    'timestamp': datetime.now().isoformat()
                })
                
                if alerts:
                    self.socketio.emit('alerts', alerts)
                
                self.socketio.emit('ai_decision', {
                    'action': action.value,
                    'message': message,
                    'details': details,
                    'timestamp': datetime.now().isoformat()
                })
                
                # إرسال تحديثات دورية للبيانات التاريخية
                historical_data = self.data_logger.get_tank_data(limit=50)
                self.socketio.emit('historical_update', historical_data)
                
                time.sleep(update_interval)
                
            except Exception as e:
                print(f"Error in simulation loop: {e}")
                time.sleep(update_interval)