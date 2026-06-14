"""
Operations Logbook Service
Tracks all AI analyses, incidents, and engineer feedback.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from backend.src.database import get_connection

logger = logging.getLogger(__name__)


class LogbookService:
    """Service for managing operations logbook entries and feedback."""
    
    @staticmethod
    def create_incident(
        equipment_id: str,
        equipment_name: str,
        sensor_readings: Dict[str, Any]
    ) -> str:
        """Create incident record."""
        incident_id = f"INC-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO incidents (incident_id, equipment_id, equipment_name, sensor_readings, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            incident_id,
            equipment_id,
            equipment_name,
            json.dumps(sensor_readings),
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created incident: {incident_id}")
        return incident_id
    
    @staticmethod
    def create_entry(
        equipment_name: str,
        fault_description: str,
        root_cause: str,
        risk_level: str,
        urgency_hours: int,
        immediate_actions: str,
        repair_steps: str = "",
        long_term_recommendations: str = "",
        evidence_sources: str = "",
        confidence_score: float = 0.0,
        incident_id: str = None
    ) -> str:
        """Create logbook entry."""
        entry_id = f"LOG-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO logbook_entries 
            (entry_id, incident_id, equipment_name, fault_description, root_cause, 
             risk_level, urgency_hours, immediate_actions, repair_steps, 
             long_term_recommendations, evidence_sources, confidence_score, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry_id, incident_id, equipment_name, fault_description, root_cause,
            risk_level, urgency_hours, immediate_actions, repair_steps,
            long_term_recommendations, evidence_sources, confidence_score,
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created logbook entry: {entry_id}")
        return entry_id
    
    @staticmethod
    def get_entries(
        equipment_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get logbook entries with optional filters."""
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM logbook_entries WHERE 1=1"
        params = []
        
        if equipment_filter:
            query += " AND equipment_name LIKE ?"
            params.append(f"%{equipment_filter}%")
        
        if status_filter:
            query += " AND status = ?"
            params.append(status_filter)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_entry(entry_id: str) -> Optional[Dict[str, Any]]:
        """Get single logbook entry with feedback history."""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get entry
        cursor.execute("SELECT * FROM logbook_entries WHERE entry_id = ?", (entry_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        entry = dict(row)
        
        # Get feedback
        cursor.execute("""
            SELECT * FROM feedback 
            WHERE entry_id = ? 
            ORDER BY submitted_at DESC
        """, (entry_id,))
        
        feedback_rows = cursor.fetchall()
        entry['feedback_history'] = [dict(f) for f in feedback_rows]
        
        conn.close()
        return entry
    
    @staticmethod
    def submit_feedback(
        entry_id: str,
        verdict: str,
        actual_root_cause: str = None,
        action_taken: str = None,
        outcome: str = None,
        downtime_hours: float = None,
        engineer_notes: str = None
    ) -> int:
        """Submit engineer feedback on logbook entry."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO feedback 
            (entry_id, verdict, actual_root_cause, action_taken, outcome, 
             downtime_hours, engineer_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            entry_id, verdict, actual_root_cause, action_taken,
            outcome, downtime_hours, engineer_notes
        ))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Submitted feedback for {entry_id}: {verdict}")
        return feedback_id
    
    @staticmethod
    def update_entry_status(entry_id: str, status: str):
        """Update entry status (OPEN/RESOLVED)."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE logbook_entries SET status = ? WHERE entry_id = ?
        """, (status, entry_id))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_feedback_stats() -> Dict[str, Any]:
        """Get feedback statistics."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN verdict = 'confirmed' THEN 1 ELSE 0 END) as confirmed,
                SUM(CASE WHEN verdict = 'incorrect' THEN 1 ELSE 0 END) as incorrect
            FROM feedback
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if not row or row['total'] == 0:
            return {"total": 0, "confirmed": 0, "incorrect": 0, "accuracy": 0.0}
        
        total = row['total']
        confirmed = row['confirmed']
        incorrect = row['incorrect']
        accuracy = (confirmed / total * 100) if total > 0 else 0.0
        
        return {
            "total": total,
            "confirmed": confirmed,
            "incorrect": incorrect,
            "accuracy": round(accuracy, 1)
        }
    
    @staticmethod
    def create_report(
        incident_id: str,
        entry_id: str,
        report_data: Dict[str, Any]
    ) -> str:
        """Store structured report."""
        report_id = f"RPT-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO reports (report_id, incident_id, entry_id, report_data)
            VALUES (?, ?, ?, ?)
        """, (
            report_id, incident_id, entry_id, json.dumps(report_data)
        ))
        
        conn.commit()
        conn.close()
        
        return report_id
    
    @staticmethod
    def get_reports(limit: int = 50) -> List[Dict[str, Any]]:
        """Get analysis reports."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM reports 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        reports = []
        for row in rows:
            report = dict(row)
            report['report_data'] = json.loads(report['report_data'])
            reports.append(report)
        
        return reports


# Singleton
_service: Optional[LogbookService] = None

def get_logbook_service() -> LogbookService:
    global _service
    if _service is None:
        _service = LogbookService()
    return _service
