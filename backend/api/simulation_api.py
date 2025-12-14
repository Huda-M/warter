from flask import Blueprint, jsonify, request
import yaml
import json
from pathlib import Path
import sys

# إضافة المسار
sys.path.insert(0, str(Path(__file__).parent.parent))

# إنشاء Blueprint
simulation_bp = Blueprint('simulation', __name__)

SCENARIOS_DIR = Path(__file__).parent.parent / "simulation" / "scenarios"
CONFIGS_DIR = Path(__file__).parent.parent / "simulation" / "configs"

@simulation_bp.route('/scenarios', methods=['GET'])
def list_scenarios():
    """قائمة سيناريوهات المحاكاة المتاحة"""
    scenarios = []
    if SCENARIOS_DIR.exists():
        for file in SCENARIOS_DIR.glob("*.yaml"):
            scenarios.append(file.stem)
    return jsonify(scenarios)

@simulation_bp.route('/scenarios/<name>', methods=['GET'])
def get_scenario(name):
    """الحصول على سيناريو محدد"""
    file_path = SCENARIOS_DIR / f"{name}.yaml"
    if not file_path.exists():
        return jsonify({"error": "Scenario not found"}), 404
    
    with open(file_path, 'r', encoding='utf-8') as f:
        scenario = yaml.safe_load(f)
    
    return jsonify(scenario)

@simulation_bp.route('/scenarios/<name>/run', methods=['POST'])
def run_scenario(name):
    """تشغيل سيناريو محاكاة"""
    # هنا يمكن تنفيذ السيناريو
    return jsonify({"success": True, "scenario": name, "status": "started"})

@simulation_bp.route('/configs', methods=['GET'])
def get_configs():
    """الحصول على تكوينات المحاكاة"""
    configs = {}
    if CONFIGS_DIR.exists():
        for file in CONFIGS_DIR.glob("*.json"):
            with open(file, 'r', encoding='utf-8') as f:
                configs[file.stem] = json.load(f)
    
    return jsonify(configs)

@simulation_bp.route('/status', methods=['GET'])
def get_status():
    """الحصول على حالة المحاكاة"""
    return jsonify({
        "running": True,
        "time_scale": 1.0,
        "current_scenario": None
    })

@simulation_bp.route('/control', methods=['POST'])
def control_simulation():
    """التحكم في المحاكاة"""
    data = request.json
    action = data.get('action', 'start')
    
    return jsonify({
        "success": True,
        "action": action,
        "status": "executed"
    })

@simulation_bp.route('/export', methods=['POST'])
def export_simulation():
    """تصدير بيانات المحاكاة"""
    data = request.json
    format_type = data.get('format', 'json')
    include_history = data.get('include_history', True)
    
    return jsonify({
        "success": True,
        "format": format_type,
        "data": {}
    })