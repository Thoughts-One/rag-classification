import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Optional
import json
import os

class ClassificationCache:
    def __init__(self):
        db_path = os.getenv("DATABASE_URL", "rag_classification.db")
        self.conn = sqlite3.connect(db_path)
        self.ttl = timedelta(hours=int(os.getenv("CACHE_TTL_HOURS", "24")))
        self._init_db()

    def _init_db(self):
        """Initialize database tables if they don't exist"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classification_cache (
                key TEXT PRIMARY KEY,
                value TEXT,
                expires_at TIMESTAMP
            )
        """)
        self.conn.commit()

    def get(self, key: str) -> Optional[Dict]:
        """Get cached classification result"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT value FROM classification_cache WHERE key = ? AND (expires_at IS NULL OR expires_at > ?)",
            (key, datetime.utcnow())
        )
        result = cursor.fetchone()
        if result:
            return json.loads(result[0])
        return None

    def set(self, key: str, value: Dict) -> None:
        """Cache classification result"""
        expires_at = datetime.utcnow() + self.ttl if self.ttl else None
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO classification_cache 
            (key, value, expires_at)
            VALUES (?, ?, ?)
            """,
            (key, json.dumps(value), expires_at)
        )
        self.conn.commit()

    def clear(self, pattern: str = "*") -> int:
        """Clear cache entries matching pattern"""
        cursor = self.conn.cursor()
        if pattern == "*":
            cursor.execute("DELETE FROM classification_cache")
        else:
            cursor.execute(
                "DELETE FROM classification_cache WHERE key LIKE ?",
                (pattern.replace("*", "%"),)
            )
        self.conn.commit()
        return cursor.rowcount

    def __del__(self):
        """Close database connection when instance is destroyed"""
        if hasattr(self, 'conn'):
            self.conn.close()