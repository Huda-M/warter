# import sys
# from pathlib import Path
# sys.path.insert(0, str(Path(__file__).parent.parent))

# from models.tank_model import WaterTank
# from models.ai_decision import AIDecisionMaker
# from .tank_api import tank, ai

# @control_bp.route('/mode', methods=['POST'])
# def switch_mode():
#     """تبديل وضع التحكم (يدوي/آلي)"""
#     data = request.json
#     ai_mode = data.get('ai_mode', True)
#     tank.ai_mode = ai_mode
#     return jsonify({"success": True, "ai_mode": ai_mode})

# @control_bp.route('/config', methods=['POST'])
# def update_config():
#     """تحديث إعدادات التحكم"""
#     data = request.json
    
#     if 'target_level' in data:
#         ai.config.target_level = data['target_level']
    
#     if 'flow_rate' in data:
#         tank.set_flow_rate(data['flow_rate'])
    
#     return jsonify({
#         "success": True,
#         "config": {
#             "target_level": ai.config.target_level,
#             "flow_rate": tank.flow_rate
#         }
#     })

# @control_bp.route('/ai/logs', methods=['GET'])
# def get_ai_logs():
#     """الحصول على سجلات الذكاء الاصطناعي"""
#     limit = request.args.get('limit', default=20, type=int)
#     logs = ai.get_recent_logs(limit)
#     return jsonify({"success": True, "data": logs})

# @control_bp.route('/simulate/leak', methods=['POST'])
# def simulate_leak():
#     """محاكاة تسرب المياه"""
#     data = request.json
#     active = data.get('active', True)
#     tank.simulate_leak(active)
#     return jsonify({"success": True, "leak_detected": active})

# @control_bp.route('/reset', methods=['POST'])
# def reset_tank():
#     """إعادة ضبط الخزان"""
#     tank.reset()
#     return jsonify({"success": True, "message": "Tank reset successfully"})
from flask import Blueprint, jsonify, request
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.tank_model import WaterTank
from models.ai_decision import AIDecisionMaker

# إنشاء Blueprint أولاً
control_bp = Blueprint('control', __name__)

# استيراد المثيلات من tank_api
from api.tank_api import tank, ai

@control_bp.route('/fill', methods=['POST'])
def start_filling():
    """بدء عملية ملء الخزان"""
    tank.set_fill(True)
    return jsonify({"success": True, "is_filling": True})

@control_bp.route('/drain', methods=['POST'])
def start_draining():
    """بدء عملية تفريغ الخزان"""
    tank.set_drain(True)
    return jsonify({"success": True, "is_draining": True})

@control_bp.route('/stop', methods=['POST'])
def stop_all():
    """إيقاف جميع العمليات"""
    tank.set_fill(False)
    tank.set_drain(False)
    return jsonify({"success": True, "is_filling": False, "is_draining": False})

@control_bp.route('/flow_rate', methods=['POST'])
def set_flow_rate():
    """تعيين معدل التدفق"""
    data = request.json
    rate = data.get('rate', 20)
    tank.set_flow_rate(rate)
    return jsonify({"success": True, "flow_rate": tank.flow_rate})

@control_bp.route('/target', methods=['POST'])
def set_target_level():
    """تعيين مستوى الهدف"""
    data = request.json
    target = data.get('target', 80)
    ai.config.target_level = target
    return jsonify({"success": True, "target_level": ai.config.target_level})

@control_bp.route('/ai/decision', methods=['GET'])
def get_ai_decision():
    """الحصول على قرار الذكاء الاصطناعي"""
    state = tank.get_state()
    history = tank.get_history(20)
    action, message, details = ai.analyze(state, history)
    return jsonify({
        "action": action.value,
        "message": message,
        "details": details
    })