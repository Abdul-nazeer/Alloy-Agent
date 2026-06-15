"""
Sensor Routes - Expose sensor data and equipment information
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

from backend.src.services.sensor_data_service import get_sensor_service

router = APIRouter(prefix="/api/sensors", tags=["Sensors"])


# ══════════════════════════════════════════════════════════════════════
# RESPONSE MODELS
# ══════════════════════════════════════════════════════════════════════

class EquipmentInfo(BaseModel):
    """Equipment specification"""
    equipment_id: str
    equipment_type: str
    location: str
    install_date: str
    last_maintenance: str
    operating_hours: int
    status: str


class SensorReading(BaseModel):
    """Single sensor reading"""
    equipment_id: str
    timestamp: str
    temperature_c: float
    pressure_bar: float
    vibration_mm_s: float
    current_a: float
    rpm: float


class TrendAnalysis(BaseModel):
    """Trend analysis for a sensor"""
    sensor: str
    trend: str  # increasing, decreasing, stable
    change_rate: float
    first_value: Optional[float] = None
    last_value: Optional[float] = None
    data_points: int
    time_range_hours: int


class MaintenanceLog(BaseModel):
    """Maintenance log entry"""
    log_id: str
    equipment_id: str
    timestamp: str
    event_type: str
    description: str
    parts_used: str
    cost: float
    downtime_hours: float
    engineer: str


# ══════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════════════════

@router.get("/equipment", response_model=List[EquipmentInfo])
async def get_all_equipment():
    """Get all equipment with current status"""
    try:
        service = get_sensor_service()
        equipment = service.get_all_equipment()
        return equipment
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching equipment: {str(e)}")


@router.get("/equipment/{equipment_id}", response_model=EquipmentInfo)
async def get_equipment(equipment_id: str):
    """Get specific equipment by ID"""
    try:
        service = get_sensor_service()
        equipment = service.get_equipment_by_id(equipment_id)
        
        if not equipment:
            raise HTTPException(status_code=404, detail=f"Equipment {equipment_id} not found")
        
        return equipment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching equipment: {str(e)}")


@router.get("/equipment/{equipment_id}/history", response_model=List[SensorReading])
async def get_sensor_history(
    equipment_id: str,
    hours: int = Query(24, ge=1, le=168, description="Hours of history (max 7 days)")
):
    """Get historical sensor readings for equipment"""
    try:
        service = get_sensor_service()
        
        # Check if equipment exists
        equipment = service.get_equipment_by_id(equipment_id)
        if not equipment:
            raise HTTPException(status_code=404, detail=f"Equipment {equipment_id} not found")
        
        # Get history
        history = service.get_sensor_history(equipment_id, hours=hours)
        
        return history
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sensor history: {str(e)}")


@router.get("/equipment/{equipment_id}/latest", response_model=SensorReading)
async def get_latest_reading(equipment_id: str):
    """Get most recent sensor reading for equipment"""
    try:
        service = get_sensor_service()
        
        reading = service.get_latest_reading(equipment_id)
        if not reading:
            raise HTTPException(status_code=404, detail=f"No readings found for {equipment_id}")
        
        return reading
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching latest reading: {str(e)}")


@router.get("/equipment/{equipment_id}/trend/{sensor_name}", response_model=TrendAnalysis)
async def get_sensor_trend(
    equipment_id: str,
    sensor_name: str,
    hours: int = Query(24, ge=1, le=168, description="Hours to analyze")
):
    """
    Calculate trend for a specific sensor over time.
    sensor_name options: temperature_c, pressure_bar, vibration_mm_s, current_a, rpm
    """
    try:
        service = get_sensor_service()
        
        # Check if equipment exists
        equipment = service.get_equipment_by_id(equipment_id)
        if not equipment:
            raise HTTPException(status_code=404, detail=f"Equipment {equipment_id} not found")
        
        # Calculate trend
        trend = service.calculate_trend(equipment_id, sensor_name, hours=hours)
        
        return trend
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating trend: {str(e)}")


@router.get("/maintenance/logs", response_model=List[MaintenanceLog])
async def get_maintenance_logs(
    equipment_id: Optional[str] = Query(None, description="Filter by equipment ID"),
    days: int = Query(30, ge=1, le=365, description="Days of history")
):
    """Get maintenance logs, optionally filtered by equipment"""
    try:
        service = get_sensor_service()
        logs = service.get_maintenance_logs(equipment_id=equipment_id, days=days)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching maintenance logs: {str(e)}")


@router.get("/health")
async def sensor_health():
    """Check if sensor data service is operational"""
    try:
        service = get_sensor_service()
        equipment_count = len(service.get_all_equipment())
        
        return {
            "status": "healthy",
            "equipment_count": equipment_count,
            "data_loaded": equipment_count > 0
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Sensor service unhealthy: {str(e)}")



@router.get("/stream/status")
async def get_stream_status():
    """Get WebSocket streaming status and available equipment"""
    from backend.src.services.sensor_simulator import get_sensor_simulator
    
    simulator = get_sensor_simulator()
    equipment_ids = simulator.get_all_equipment_ids()
    
    return {
        "status": "available",
        "equipment": equipment_ids,
        "websocket_url": "ws://localhost:8000/ws/sensors/{equipment_id}",
        "interval_seconds": 15,
        "features": [
            "Real-time sensor readings every 15 seconds",
            "Automatic anomaly detection",
            "Threshold violation alerts",
            "Normal/healthy data by default",
            "Demo anomaly button for AI showcase"
        ]
    }


@router.get("/api-usage")
async def get_api_usage():
    """Get current API usage statistics and configuration"""
    from backend.src.services.api_config import get_api_usage_stats, get_api_config
    
    stats = get_api_usage_stats()
    config = get_api_config()
    
    return {
        "usage": stats,
        "configuration": {
            "mode": config.get("description", "Unknown"),
            "cooldowns": config.get("cooldowns", {}),
            "ai_enabled_for": config.get("use_ai_for", []),
            "caching_enabled": config.get("enable_caching", False),
        },
        "tips": [
            "Set API_USAGE_MODE=conservative to minimize API calls",
            "Set API_USAGE_MODE=production for highest quality reports",
            "Default 'balanced' mode is optimized for free tier Groq API"
        ]
    }


@router.post("/demo-anomaly")
async def trigger_demo_anomaly(equipment_id: str = "AC-001"):
    """
    Trigger a CRITICAL anomaly for demonstration purposes
    
    This endpoint is called when user clicks "DEMO ANOMALY" button.
    It injects a critical fault and triggers AI analysis.
    
    Args:
        equipment_id: Equipment to inject anomaly (default: AC-001 Air Compressor)
    
    Returns:
        Sensor reading with anomaly and AI analysis report
    """
    from backend.src.services.sensor_simulator import get_sensor_simulator
    from backend.src.services.auto_report_generator import get_report_generator
    from backend.src.agents.agent_api import chat
    
    try:
        # Generate critical anomaly
        simulator = get_sensor_simulator()
        reading = simulator.trigger_demo_anomaly(equipment_id)
        
        # Trigger AI analysis immediately (bypass cooldown for demo)
        report_gen = get_report_generator()
        await report_gen.process_sensor_reading(reading)
        
        # Generate chat-style AI response
        anomaly_description = "; ".join([a['message'] for a in reading.get('anomalies', [])])
        
        ai_response = chat(
            query=f"Analyze this CRITICAL issue: {anomaly_description}",
            equipment_id=equipment_id,
            equipment_type=reading['equipment_type'],
            sensor_data={
                'temperature_c': reading.get('temperature_c'),
                'pressure_bar': reading.get('pressure_bar'),
                'vibration_mm_s': reading.get('vibration_mm_s'),
                'current_a': reading.get('current_a'),
            },
            user_role="supervisor"
        )
        
        return {
            "success": True,
            "sensor_reading": reading,
            "ai_analysis": ai_response,
            "message": f"Demo anomaly triggered on {equipment_id}. AI analysis complete.",
            "severity": "CRITICAL",
            "report_generated": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger demo anomaly: {str(e)}")
