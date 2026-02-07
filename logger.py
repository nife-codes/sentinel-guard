"""
Audit logger with SQLite backend
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json
import config


class AuditLogger:
    """SQLite-based audit logger for tracking all decisions"""
    
    def __init__(self, db_path: str = config.DB_PATH):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the audit log database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_id TEXT NOT NULL,
                prompt TEXT NOT NULL,
                decision TEXT NOT NULL,
                confidence REAL NOT NULL,
                reasons TEXT NOT NULL,
                attacks_detected TEXT,
                temporal_flags TEXT,
                sanitized_prompt TEXT
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_timestamp 
            ON audit_log(user_id, timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_decision 
            ON audit_log(decision)
        """)
        
        conn.commit()
        conn.close()
    
    def log_decision(self, user_id: str, prompt: str, decision: str, 
                    confidence: float, reasons: List[str], 
                    attacks_detected: List[str] = None,
                    temporal_flags: List[str] = None,
                    sanitized_prompt: str = None) -> int:
        """
        Log a decision to the audit trail
        Returns: log entry ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_log 
            (timestamp, user_id, prompt, decision, confidence, reasons, 
             attacks_detected, temporal_flags, sanitized_prompt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat(),
            user_id,
            prompt,
            decision,
            confidence,
            json.dumps(reasons),
            json.dumps(attacks_detected or []),
            json.dumps(temporal_flags or []),
            sanitized_prompt
        ))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return log_id
    
    def get_user_logs(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get audit logs for a specific user"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM audit_log 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_blocked_prompts(self, limit: int = 100) -> List[Dict]:
        """Get all blocked prompts"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM audit_log 
            WHERE decision = 'BLOCK' 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_statistics(self) -> Dict[str, any]:
        """Get overall statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total counts by decision
        cursor.execute("""
            SELECT decision, COUNT(*) as count 
            FROM audit_log 
            GROUP BY decision
        """)
        decision_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Total logs
        cursor.execute("SELECT COUNT(*) FROM audit_log")
        total_logs = cursor.fetchone()[0]
        
        # Unique users
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM audit_log")
        unique_users = cursor.fetchone()[0]
        
        # Average confidence by decision
        cursor.execute("""
            SELECT decision, AVG(confidence) as avg_confidence 
            FROM audit_log 
            GROUP BY decision
        """)
        avg_confidence = {row[0]: round(row[1], 2) for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "total_logs": total_logs,
            "unique_users": unique_users,
            "decision_counts": decision_counts,
            "average_confidence": avg_confidence
        }
    
    def clear_logs(self, user_id: Optional[str] = None):
        """Clear logs (optionally for a specific user)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute("DELETE FROM audit_log WHERE user_id = ?", (user_id,))
        else:
            cursor.execute("DELETE FROM audit_log")
        
        conn.commit()
        conn.close()


# Global logger instance
audit_logger = AuditLogger()
