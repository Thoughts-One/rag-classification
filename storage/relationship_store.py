from typing import Dict, List
import sqlite3
from datetime import datetime
import os

class RelationshipStore:
    def __init__(self):
        db_path = os.getenv("DATABASE_URL", "rag_classification.db")
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        """Initialize database tables if they don't exist"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                document_id TEXT,
                relationship_type TEXT,
                target TEXT,
                created_at TIMESTAMP,
                PRIMARY KEY (document_id, relationship_type, target)
            )
        """)
        self.conn.commit()

    def store(self, document_id: str, relationships: Dict[str, List[str]]) -> None:
        """Store relationship metadata for a document"""
        cursor = self.conn.cursor()
        timestamp = datetime.utcnow()
        
        for rel_type, targets in relationships.items():
            for target in targets:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO relationships 
                    (document_id, relationship_type, target, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (document_id, rel_type, target, timestamp)
                )
        
        self.conn.commit()

    def get_relationships(self, document_id: str) -> Dict[str, List[str]]:
        """Get all relationships for a document"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT relationship_type, target FROM relationships WHERE document_id = ?",
            (document_id,)
        )
        
        results = {}
        for rel_type, target in cursor.fetchall():
            if rel_type not in results:
                results[rel_type] = []
            results[rel_type].append(target)
            
        return results

    def query_relationships(self, filters: Dict) -> List[Dict]:
        """Query relationships by criteria"""
        query = "SELECT document_id, relationship_type, target FROM relationships WHERE 1=1"
        params = []
        
        if "document_id" in filters:
            query += " AND document_id = ?"
            params.append(filters["document_id"])
            
        if "relationship_type" in filters:
            query += " AND relationship_type = ?"
            params.append(filters["relationship_type"])
            
        if "target" in filters:
            query += " AND target LIKE ?"
            params.append(f"%{filters['target']}%")
            
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        
        return [
            {
                "document_id": row[0],
                "relationship_type": row[1],
                "target": row[2]
            }
            for row in cursor.fetchall()
        ]