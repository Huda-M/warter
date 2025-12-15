import sqlite3
from datetime import datetime
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

class DataLogger:
    def __init__(self, db_path="data/historical_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """تهيئة قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول قراءات الخزان
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tank_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                water_level REAL,
                water_volume REAL,
                temperature REAL,
                pressure REAL,
                ph_level REAL,
                turbidity REAL,
                is_filling BOOLEAN,
                is_draining BOOLEAN,
                leak_detected BOOLEAN,
                flow_rate REAL
            )
        ''')
        
        # جدول سجلات الذكاء الاصطناعي
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                message TEXT,
                log_type TEXT,
                details TEXT
            )
        ''')


        # جدول التنبيهات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                alert_type TEXT,
                severity TEXT,
                message TEXT,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized successfully")
    
    def log_tank_data(self, tank_state):
        """تسجيل بيانات الخزان"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO tank_readings 
                (water_level, water_volume, temperature, pressure, ph_level, turbidity, 
                 is_filling, is_draining, leak_detected, flow_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                tank_state['water_level'],
                tank_state['water_volume'],
                tank_state['temperature'],
                tank_state['pressure'],
                tank_state['ph_level'],
                tank_state['turbidity'],
                tank_state['is_filling'],
                tank_state['is_draining'],
                tank_state['leak_detected'],
                tank_state['flow_rate']
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error logging tank data: {e}")
    
    def log_ai_message(self, message, log_type="info", details=None):
        """تسجيل رسالة من الذكاء الاصطناعي"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # تحويل details لـ JSON إذا كان موجوداً
            details_json = json.dumps(details) if details else None
            
            cursor.execute('''
                INSERT INTO ai_logs (message, log_type, details)
                VALUES (?, ?, ?)
            ''', (message, log_type, details_json))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error logging AI message: {e}")
    
    def log_alert(self, alert_type, severity, message):
        """تسجيل تنبيه"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts (alert_type, severity, message)
                VALUES (?, ?, ?)
            ''', (alert_type, severity, message))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error logging alert: {e}")
    
    def get_tank_data(self, limit=1000, start_time=None, end_time=None):
        """الحصول على بيانات الخزان التاريخية"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM tank_readings"
            params = []
            
            conditions = []
            if start_time:
                conditions.append("timestamp >= ?")
                params.append(start_time)
            if end_time:
                conditions.append("timestamp <= ?")
                params.append(end_time)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return data
        except Exception as e:
            logger.error(f"Error getting tank data: {e}")
            return []
    
    def get_ai_logs(self, limit=100):
        """الحصول على سجلات الذكاء الاصطناعي"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM ai_logs 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return data
        except Exception as e:
            logger.error(f"Error getting AI logs: {e}")
            return []
    
    def get_alerts(self, unresolved_only=True, limit=50, severity=None):
        """الحصول على التنبيهات"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM alerts"
            params = []
            conditions = []
            
            if unresolved_only:
                conditions.append("resolved = FALSE")
            
            if severity:
                conditions.append("severity = ?")
                params.append(severity)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return data
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []
    
    def resolve_alert(self, alert_id):
        """تعليم تنبيه كمحلول"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE alerts SET resolved = TRUE WHERE id = ?
            ''', (alert_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return False