"""
Reports and Logbook API Routes
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
import json
from datetime import datetime, timedelta
from backend.src.database.schema import get_connection

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/list")
async def get_reports(equipment_id: Optional[str] = None, days: int = 30):
    """Get all reports from database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT r.report_id, r.report_data, r.created_at, 
                   i.equipment_id, i.equipment_name
            FROM reports r
            LEFT JOIN incidents i ON r.incident_id = i.incident_id
            WHERE r.created_at >= datetime('now', '-' || ? || ' days')
        """
        params = [days]
        
        if equipment_id:
            query += " AND i.equipment_id = ?"
            params.append(equipment_id)
        
        query += " ORDER BY r.created_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        reports = []
        for row in rows:
            report_data = json.loads(row['report_data']) if row['report_data'] else {}
            reports.append({
                "id": row['report_id'],
                "equipment_id": row['equipment_id'],
                "equipment_name": row['equipment_name'],
                "title": report_data.get('title', 'Analysis Report'),
                "status": report_data.get('risk_level', 'normal').lower(),
                "findings": report_data.get('summary', 'No summary available'),
                "content": report_data.get('content', ''),
                "date": row['created_at'],
            })
        
        return {"reports": reports, "count": len(reports)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logbook")
async def get_logbook_entries(
    equipment_id: Optional[str] = None, 
    status: Optional[str] = None,
    days: int = 30
):
    """Get logbook entries from database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT entry_id, equipment_name, fault_description, root_cause,
                   risk_level, status, timestamp, created_at
            FROM logbook_entries
            WHERE created_at >= datetime('now', '-' || ? || ' days')
        """
        params = [days]
        
        if equipment_id:
            query += " AND equipment_name LIKE ?"
            params.append(f"%{equipment_id}%")
        
        if status:
            query += " AND status = ?"
            params.append(status.upper())
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        entries = []
        for row in rows:
            entries.append({
                "id": row['entry_id'],
                "equipment": row['equipment_name'],
                "event": "Anomaly Detected" if "anomaly" in (row['fault_description'] or '').lower() else "Maintenance Activity",
                "engineer": "AI System",
                "notes": row['fault_description'] or row['root_cause'] or "No details",
                "time": row['timestamp'] or row['created_at'],
                "type": "alert" if row['risk_level'] in ['CRITICAL', 'HIGH'] else "maintenance",
                "status": row['status'] or "OPEN"
            })
        
        return {"entries": entries, "count": len(entries)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_report(equipment_id: str, report_type: str = "health_summary"):
    """Generate a new report using AI agents"""
    try:
        from backend.src.agents.agent_api import chat
        from backend.src.database.schema import get_connection
        import uuid
        
        # Generate report using AI
        query_map = {
            "health_summary": f"Generate equipment health summary for {equipment_id}",
            "maintenance_forecast": f"Predict maintenance needs for {equipment_id} in next 30 days",
            "performance": f"Generate performance analysis for {equipment_id}"
        }
        
        query = query_map.get(report_type, query_map["health_summary"])
        
        # Call AI agent
        response = chat(query=query, equipment_id=equipment_id, user_role="manager")
        
        # Store in database
        report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"
        report_data = {
            "title": report_type.replace('_', ' ').title(),
            "risk_level": response.get('risk_level', 'NORMAL'),
            "summary": response.get('answer', ''),
            "content": response.get('report', response.get('answer', '')),
            "agents_used": response.get('agents_used', []),
        }
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reports (report_id, report_data, created_at)
            VALUES (?, ?, ?)
        """, (report_id, json.dumps(report_data), datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "report_id": report_id,
            "message": "Report generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
