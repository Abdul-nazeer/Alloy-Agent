"""
Agent Tools — Functions that agents can call
"""

import logging
from typing import Optional
from backend.src.rag import get_rag_pipeline
from backend.src.agents.state import RAGResult, ThresholdCheck, SensorReading

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# RAG Retrieval Tool
# ══════════════════════════════════════════════════════════════════════════════

def rag_retrieve(
    query: str,
    top_k: int = 5,
    doc_ids: Optional[list[str]] = None
) -> RAGResult:
    """
    Retrieve relevant knowledge from RAG system.
    
    Args:
        query: Search query
        top_k: Number of results
        doc_ids: Optional filter to specific documents
    
    Returns:
        RAGResult with chunks, sources, and formatted context
    """
    try:
        rag = get_rag_pipeline()
        result = rag.query(query, top_k=top_k)
        
        return RAGResult(
            chunks=result.get("retrieved_chunks", []),
            sources=result.get("sources", []),
            grounded=result.get("grounded", False),
            num_results=result.get("num_results", 0),
            context=result.get("context", ""),
        )
    except Exception as e:
        logger.error(f"RAG retrieval failed: {e}")
        return RAGResult(
            chunks=[],
            sources=[],
            grounded=False,
            num_results=0,
            context="",
        )


# ══════════════════════════════════════════════════════════════════════════════
# Threshold Lookup Tool
# ══════════════════════════════════════════════════════════════════════════════

# Equipment-specific thresholds (in production, load from database)
THRESHOLDS = {
    "Air Compressor": {
        "TEMP": ThresholdCheck("TEMP", 60, 90, 90, 100, "°C"),
        "VIB": ThresholdCheck("VIB", 0.5, 2.5, 2.5, 4.0, "mm/s"),
        "PRES": ThresholdCheck("PRES", 6.5, 7.5, 6.0, 5.5, "bar"),
        "CURR": ThresholdCheck("CURR", 20, 50, 55, 65, "A"),
    },
    "Cooling Fan System": {
        "TEMP": ThresholdCheck("TEMP", 40, 70, 75, 85, "°C"),
        "VIB": ThresholdCheck("VIB", 0.3, 1.8, 2.0, 3.0, "mm/s"),
        "RPM": ThresholdCheck("RPM", 1400, 1500, 1600, 1700, "RPM"),
        "CURR": ThresholdCheck("CURR", 5, 15, 18, 22, "A"),
    },
    "Rolling Mill": {
        "TEMP": ThresholdCheck("TEMP", 70, 110, 120, 140, "°C"),
        "VIB": ThresholdCheck("VIB", 1.0, 4.0, 5.0, 7.0, "mm/s"),
        "PRES": ThresholdCheck("PRES", 150, 200, 210, 230, "bar"),
        "TORQUE": ThresholdCheck("TORQUE", 5000, 8000, 8500, 9500, "Nm"),
    },
    "Conveyor Motor": {
        "TEMP": ThresholdCheck("TEMP", 50, 80, 85, 95, "°C"),
        "VIB": ThresholdCheck("VIB", 0.4, 2.0, 2.5, 3.5, "mm/s"),
        "CURR": ThresholdCheck("CURR", 10, 30, 35, 45, "A"),
    },
    "General Industrial Motor": {
        "TEMP": ThresholdCheck("TEMP", 50, 75, 90, 110, "°C"),
        "VIB": ThresholdCheck("VIB", 0.5, 2.0, 3.0, 4.5, "mm/s"),
        "CURR": ThresholdCheck("CURR", 15, 40, 50, 60, "A"),
    },
}


def threshold_lookup(
    equipment_type: str,
    sensor_type: str
) -> Optional[ThresholdCheck]:
    """
    Get equipment-specific thresholds.
    
    Args:
        equipment_type: Type of equipment
        sensor_type: Sensor type (TEMP, VIB, PRES, etc.)
    
    Returns:
        ThresholdCheck or None if not found
    """
    equipment_thresholds = THRESHOLDS.get(equipment_type, {})
    return equipment_thresholds.get(sensor_type)


# ══════════════════════════════════════════════════════════════════════════════
# Spare Parts Lookup Tool
# ══════════════════════════════════════════════════════════════════════════════

def spare_parts_lookup(equipment_type: str = None, part_keyword: str = None) -> list[dict]:
    """
    Lookup spare parts from database.
    
    Args:
        equipment_type: Filter by equipment type (e.g., "Air Compressor")
        part_keyword: Search keyword in part name (e.g., "bearing", "valve")
    
    Returns:
        List of matching spare parts with availability info
    """
    from backend.src.database.schema import get_connection
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Build query
        query = "SELECT * FROM spare_parts WHERE 1=1"
        params = []
        
        if equipment_type:
            query += " AND equipment_type = ?"
            params.append(equipment_type)
        
        if part_keyword:
            query += " AND (part_name LIKE ? OR part_id LIKE ?)"
            params.extend([f"%{part_keyword}%", f"%{part_keyword}%"])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to dict format
        parts = []
        for row in rows:
            parts.append({
                "part_number": row["part_id"],
                "description": row["part_name"],
                "in_stock": row["quantity_available"],
                "lead_time_days": row["lead_time_days"],
                "cost": row["unit_cost"],
                "status": row["status"],
                "criticality": row["criticality"],
                "supplier": row["supplier"],
            })
        
        return parts
        
    except Exception as e:
        logger.error(f"Spare parts lookup failed: {e}")
        return []


def get_critical_spare_parts(equipment_type: str) -> list[dict]:
    """
    Get critical/out-of-stock parts for an equipment type.
    
    Args:
        equipment_type: Equipment type to check
    
    Returns:
        List of parts needing procurement attention
    """
    from backend.src.database.schema import get_connection
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM spare_parts 
            WHERE equipment_type = ? 
            AND (status = 'OUT_OF_STOCK' OR status = 'LOW_STOCK')
            ORDER BY 
                CASE criticality
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'HIGH' THEN 2
                    WHEN 'MEDIUM' THEN 3
                    ELSE 4
                END
        """, (equipment_type,))
        
        rows = cursor.fetchall()
        conn.close()
        
        parts = []
        for row in rows:
            parts.append({
                "part_number": row["part_id"],
                "description": row["part_name"],
                "in_stock": row["quantity_available"],
                "lead_time_days": row["lead_time_days"],
                "cost": row["unit_cost"],
                "status": row["status"],
                "criticality": row["criticality"],
                "supplier": row["supplier"],
            })
        
        return parts
        
    except Exception as e:
        logger.error(f"Critical parts lookup failed: {e}")
        return []


# ══════════════════════════════════════════════════════════════════════════════
# Sensor Fetch Tool (Simulated)
# ══════════════════════════════════════════════════════════════════════════════

def sensor_fetch(equipment_id: str, lookback_hours: int = 24) -> list[SensorReading]:
    """
    Fetch historical sensor readings (simulated).
    
    In production, this queries your time-series database.
    
    Args:
        equipment_id: Equipment identifier
        lookback_hours: How far back to fetch
    
    Returns:
        List of historical readings
    """
    # Simulated - return empty for now
    logger.info(f"Would fetch {lookback_hours}h of sensor data for {equipment_id}")
    return []


# ══════════════════════════════════════════════════════════════════════════════
# Logbook Append Tool
# ══════════════════════════════════════════════════════════════════════════════

def logbook_append(
    equipment_id: str,
    entry_type: str,
    summary: str,
    details: dict,
    engineer: str = "AI Agent"
) -> bool:
    """
    Append entry to operations logbook.
    
    Args:
        equipment_id: Equipment ID
        entry_type: "inspection" | "maintenance" | "alert" | "diagnosis"
        summary: Brief description
        details: Full structured data
        engineer: Who made the entry
    
    Returns:
        Success boolean
    """
    import json
    from datetime import datetime
    
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "equipment_id": equipment_id,
        "type": entry_type,
        "summary": summary,
        "details": details,
        "engineer": engineer,
    }
    
    # In production: write to database
    logger.info(f"Logbook entry: {json.dumps(entry, indent=2)}")
    
    return True


# ══════════════════════════════════════════════════════════════════════════════
# Escalation Notification Tool
# ══════════════════════════════════════════════════════════════════════════════

def escalation_notify(
    equipment_id: str,
    severity: str,
    message: str,
    recipient_role: str = "supervisor"
) -> bool:
    """
    Send escalation alert to supervisor/manager.
    
    Args:
        equipment_id: Equipment in question
        severity: CRITICAL | HIGH | MEDIUM | LOW
        message: Alert message
        recipient_role: Who to notify
    
    Returns:
        Success boolean
    """
    logger.warning(f"🚨 ESCALATION [{severity}] - {equipment_id}: {message}")
    logger.warning(f"   → Notifying {recipient_role}")
    
    # In production: send email, SMS, push notification, etc.
    
    return True
