from flask import Blueprint, jsonify, request

import sys
from pathlib import Path
# إضافة المسار الأب للملف الحالي
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.tank_model import WaterTank
from models.ai_decision import AIDecisionMaker
from utils.data_logger import DataLogger

tank_bp = Blueprint('tank', __name__)

# إنشاء مثيلات
tank = WaterTank()
ai = AIDecisionMaker()
data_logger = DataLogger()

@tank_bp.route('/state', methods=['GET'])
def get_tank_state():
    """الحصول على حالة الخزان الحالية"""
    state = tank.get_state()
    return jsonify(state)

@tank_bp.route('/history', methods=['GET'])
def get_tank_history():
    """الحصول على تاريخ قراءات الخزان"""
    limit = request.args.get('limit', default=100, type=int)
    history = tank.get_history(limit)
    return jsonify(history)

@tank_bp.route('/update', methods=['POST'])
def update_tank():
    """تحديث حالة الخزان (محاكاة مرور الوقت)"""
    data = request.json
    dt = data.get('dt', 1.0)
    
    # تحديث الفيزياء
    tank.update_physics(dt)
    
    # تسجيل البيانات
    data_logger.log_tank_data(tank.get_state())
    
    return jsonify({"success": True, "state": tank.get_state()})