from flask import Blueprint, jsonify, request
from ..models.tank_model import WaterTank
from ..models.ai_decision import AIDecisionMaker

control_bp = Blueprint('control', __name__)

# نستخدم نفس المثيلات من tank_api
from .tank_api import tank, ai

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