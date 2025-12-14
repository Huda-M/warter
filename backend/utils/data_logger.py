import sqlite3
from datetime import datetime
from pathlib import Path
import json

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
                log_type TEXT
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
    
    def log_tank_data(self, tank_state):
        """تسجيل بيانات الخزان"""
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
    
    def log_ai_message(self, message, log_type="info"):
        """تسجيل رسالة من الذكاء الاصطناعي"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ai_logs (message, log_type)
            VALUES (?, ?)
        ''', (message, log_type))
        
        conn.commit()
        conn.close()
    
    def log_alert(self, alert_type, severity, message):
        """تسجيل تنبيه"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alerts (alert_type, severity, message)
            VALUES (?, ?, ?)
        ''', (alert_type, severity, message))
        
        conn.commit()
        conn.close()
    
    def get_tank_data(self, limit=1000, start_time=None, end_time=None):
        """الحصول على بيانات الخزان التاريخية"""
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
    
    def get_ai_logs(self, limit=100):
        """الحصول على سجلات الذكاء الاصطناعي"""
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
    
    def get_alerts(self, unresolved_only=True, limit=50):
        """الحصول على التنبيهات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM alerts"
        params = []
        
        if unresolved_only:
            query += " WHERE resolved = FALSE"
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return data
    
    def resolve_alert(self, alert_id):
        """تعليم تنبيه كمحلول"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE alerts SET resolved = TRUE WHERE id = ?
        ''', (alert_id,))
        
        conn.commit()
        conn.close()