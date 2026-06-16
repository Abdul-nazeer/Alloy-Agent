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
            
            # Extract all content properly
            content_obj = {
                # Core report data
                "title": report_data.get('title', 'Analysis Report'),
                "summary": report_data.get('summary', 'No summary available'),
                "content": report_data.get('content', ''),
                "report_content": report_data.get('report_content', ''),  # Full comprehensive markdown report
                
                # Structured data
                "root_causes": report_data.get('root_causes', []),
                "recommendations": report_data.get('recommendations', []),
                "anomalies": report_data.get('anomalies', []),
                "sensor_readings": report_data.get('sensor_readings', {}),
                
                # Metadata
                "risk_level": report_data.get('risk_level', 'UNKNOWN'),
                "agents_used": report_data.get('agents_used', []),
                "incident_id": report_data.get('incident_id'),
                "equipment_type": report_data.get('equipment_type'),
                "timestamp": report_data.get('timestamp'),
                
                # Role-specific summaries
                "supervisor_summary": report_data.get('supervisor_summary', ''),
                "engineer_summary": report_data.get('engineer_summary', ''),
            }
            
            reports.append({
                "id": row['report_id'],
                "equipment_id": row['equipment_id'],
                "equipment_name": row['equipment_name'],
                "title": report_data.get('title', 'Analysis Report'),
                "status": report_data.get('risk_level', 'normal').lower(),
                "findings": report_data.get('summary', 'No summary available'),
                "content": content_obj,  # Full structured content
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
    """Get comprehensive logbook entries from database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT entry_id, equipment_name, fault_description, root_cause,
                   risk_level, urgency_hours, immediate_actions, repair_steps,
                   long_term_recommendations, status, timestamp, created_at
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
            # Parse the fault_description to extract alert info
            fault_desc = row['fault_description'] or ""
            alert_line = "N/A"
            if "**Alert**:" in fault_desc:
                lines = fault_desc.split('\n')
                for line in lines:
                    if "**Alert**:" in line:
                        alert_line = line.replace("*", "").replace("Alert:", "").strip()
                        break
            
            # Parse immediate actions into list
            actions_text = row['immediate_actions'] or "N/A"
            actions_list = []
            if actions_text != "N/A" and actions_text.strip():
                for line in actions_text.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('⚠️'):
                        # Remove numbering if present
                        clean_line = line.lstrip('0123456789. ')
                        if clean_line and len(clean_line) > 5:  # Skip very short lines
                            actions_list.append(clean_line)
            
            entries.append({
                "id": row['entry_id'],
                "equipment": row['equipment_name'],
                "event": "Anomaly Detected" if "anomaly" in fault_desc.lower() else "Maintenance Activity",
                "engineer": "AI System",
                "time": row['timestamp'] or row['created_at'],
                "type": "alert" if row['risk_level'] in ['CRITICAL', 'HIGH'] else "maintenance",
                "status": row['status'] or "OPEN",
                # Comprehensive details
                "fault_description": fault_desc,
                "root_cause": row['root_cause'] or "N/A",
                "risk_level": row['risk_level'] or "MEDIUM",
                "urgency_hours": row['urgency_hours'] or 72,
                "immediate_actions": actions_list if actions_list else [],
                "repair_steps": row['repair_steps'] if row['repair_steps'] and row['repair_steps'] != "N/A" and len(row['repair_steps']) > 30 else None,
                "long_term_recommendations": row['long_term_recommendations'] if row['long_term_recommendations'] and row['long_term_recommendations'] != "N/A" and len(row['long_term_recommendations']) > 30 else None,
                "alert": alert_line,
                # Legacy fields for compatibility
                "notes": fault_desc[:200] + "..." if len(fault_desc) > 200 else fault_desc,
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
