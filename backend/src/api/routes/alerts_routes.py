"""
Alerts API Routes - Real-time notifications for autonomous monitoring
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging
from backend.src.database.schema import get_connection

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/unread")
def get_unread_alerts() -> Dict[str, Any]:
    """
    Get all unread alerts for frontend notification badge
    
    Returns:
        {
            "count": 3,
            "alerts": [
                {
                    "alert_id": "ALERT-12345678",
                    "equipment_id": "AC-001",
                    "equipment_name": "Air Compressor",
                    "severity": "CRITICAL",
                    "title": "🚨 CRITICAL Alert: AC-001",
                    "message": "4 anomalies detected. Auto-report generated.",
                    "report_id": "RPT-12345678",
                    "incident_id": "INC-12345678",
                    "created_at": "2026-06-15T10:30:00"
                }
            ]
        }
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                alert_id, equipment_id, equipment_name, alert_type,
                severity, title, message, report_id, incident_id, created_at
            FROM alerts
            WHERE is_read = 0
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        alerts = [dict(row) for row in rows]
        
        conn.close()
        
        return {
            "count": len(alerts),
            "alerts": alerts
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch unread alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
def get_all_alerts(limit: int = 50) -> Dict[str, Any]:
    """
    Get all alerts (read and unread) with pagination
    
    Args:
        limit: Maximum number of alerts to return (default 50)
    
    Returns:
        {
            "total": 127,
            "unread_count": 3,
            "alerts": [...]
        }
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as count FROM alerts")
        total = cursor.fetchone()['count']
        
        # Get unread count
        cursor.execute("SELECT COUNT(*) as count FROM alerts WHERE is_read = 0")
        unread_count = cursor.fetchone()['count']
        
        # Get alerts
        cursor.execute("""
            SELECT 
                alert_id, equipment_id, equipment_name, alert_type,
                severity, title, message, report_id, incident_id, 
                is_read, created_at
            FROM alerts
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        alerts = [dict(row) for row in rows]
        
        conn.close()
        
        return {
            "total": total,
            "unread_count": unread_count,
            "alerts": alerts
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{alert_id}/mark-read")
def mark_alert_as_read(alert_id: str) -> Dict[str, str]:
    """
    Mark a specific alert as read
    
    Args:
        alert_id: Alert ID (e.g., "ALERT-12345678")
    
    Returns:
        {"status": "ok", "alert_id": "ALERT-12345678"}
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE alerts
            SET is_read = 1
            WHERE alert_id = ?
        """, (alert_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        
        conn.commit()
        conn.close()
        
        logger.info(f"Marked alert {alert_id} as read")
        return {"status": "ok", "alert_id": alert_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mark alert as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-all-read")
def mark_all_alerts_as_read() -> Dict[str, Any]:
    """
    Mark all alerts as read
    
    Returns:
        {"status": "ok", "marked_count": 5}
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE alerts
            SET is_read = 1
            WHERE is_read = 0
        """)
        
        marked_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        logger.info(f"Marked {marked_count} alerts as read")
        return {"status": "ok", "marked_count": marked_count}
        
    except Exception as e:
        logger.error(f"Failed to mark all alerts as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{alert_id}")
def delete_alert(alert_id: str) -> Dict[str, str]:
    """
    Delete a specific alert
    
    Args:
        alert_id: Alert ID (e.g., "ALERT-12345678")
    
    Returns:
        {"status": "ok", "alert_id": "ALERT-12345678"}
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM alerts WHERE alert_id = ?", (alert_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        
        conn.commit()
        conn.close()
        
        logger.info(f"Deleted alert {alert_id}")
        return {"status": "ok", "alert_id": alert_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))
