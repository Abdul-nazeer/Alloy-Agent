"""
Agent Routes - Expose multi-agent system via FastAPI
"""
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

from backend.src.agents import chat, diagnose_equipment, check_anomalies

router = APIRouter(prefix="/api/agents", tags=["Agents"])


# ══════════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ══════════════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    """Chat with the multi-agent system"""
    message: str = Field(..., description="User message or question")
    session_id: Optional[str] = Field("default", description="Conversation session ID for memory")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What's causing the temperature spike on AC-001?",
                "session_id": "session_123"
            }
        }


class DiagnoseRequest(BaseModel):
    """Request equipment diagnosis"""
    equipment_id: str = Field(..., description="Equipment identifier")
    sensor_data: Dict[str, float] = Field(..., description="Current sensor readings")
    symptoms: Optional[List[str]] = Field(None, description="Observed symptoms")
    
    class Config:
        json_schema_extra = {
            "example": {
                "equipment_id": "AC-001",
                "sensor_data": {
                    "temperature_c": 95.5,
                    "pressure_bar": 5.2,
                    "vibration_mm_s": 8.1,
                    "current_a": 45.3,
                    "rpm": 1450
                },
                "symptoms": ["excessive heat", "unusual noise"]
            }
        }


class AnomalyCheckRequest(BaseModel):
    """Check for anomalies in sensor readings"""
    equipment_id: str = Field(..., description="Equipment identifier")
    equipment_type: str = Field(..., description="Type of equipment (e.g., Air Compressor)")
    sensor_data: Dict[str, float] = Field(..., description="Current sensor readings")
    
    class Config:
        json_schema_extra = {
            "example": {
                "equipment_id": "AC-001",
                "equipment_type": "Air Compressor",
                "sensor_data": {
                    "temperature_c": 115.5,
                    "pressure_bar": 4.2,
                    "vibration_mm_s": 12.1,
                    "current_a": 48.3,
                    "rpm": 1430
                }
            }
        }


class AgentResponse(BaseModel):
    """Standard agent response"""
    status: str = Field(..., description="Response status: success, error")
    response: str = Field(..., description="Agent's response text")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    session_id: Optional[str] = Field(None, description="Session identifier")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# ══════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════════════════

@router.post("/chat", response_model=AgentResponse)
async def agent_chat(request: ChatRequest):
    """
    Chat with the multi-agent system. Supervisor routes to appropriate specialist agents.
    Maintains conversation memory per session_id.
    """
    try:
        result = chat(
            query=request.message,
            session_id=request.session_id or "default"
        )
        
        return AgentResponse(
            status="success",
            response=result.get("answer", "No response generated"),
            metadata={
                "agents_involved": result.get("agents_used", []),
                "risk_level": result.get("risk_level"),
                "sources_count": len(result.get("sources", []))
            },
            session_id=request.session_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@router.post("/diagnose", response_model=AgentResponse)
async def diagnose(request: DiagnoseRequest):
    """
    Request equipment diagnosis. Routes through Supervisor → Diagnosis Agent → Recommendation Agent.
    Returns root causes, recommendations, and maintenance actions.
    """
    try:
        # Get equipment type from equipment_id prefix
        equipment_type = "Air Compressor"  # Default, should ideally look up from DB
        if request.equipment_id.startswith("CF"):
            equipment_type = "Cooling Fan System"
        elif request.equipment_id.startswith("RM"):
            equipment_type = "Rolling Mill"
        elif request.equipment_id.startswith("CM"):
            equipment_type = "Conveyor Motor"
        
        result = diagnose_equipment(
            equipment_id=request.equipment_id,
            equipment_type=equipment_type,
            sensor_data=request.sensor_data,
            error_codes=request.symptoms
        )
        
        return AgentResponse(
            status="success",
            response=result.get("answer", "Diagnosis completed"),
            metadata={
                "equipment_id": request.equipment_id,
                "agents_involved": result.get("agents_used", []),
                "risk_level": result.get("risk_level"),
                "root_causes_count": len(result.get("root_causes", [])),
                "recommendations_count": len(result.get("recommendations", []))
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagnosis error: {str(e)}")


@router.post("/check-anomalies", response_model=AgentResponse)
async def check_anomaly(request: AnomalyCheckRequest):
    """
    Check sensor readings for anomalies. Anomaly Agent performs:
    - Threshold violation detection
    - Multi-variate pattern analysis
    - Severity classification (NORMAL, LOW, MEDIUM, HIGH, CRITICAL)
    - Auto-escalation for CRITICAL issues
    """
    try:
        result = check_anomalies(
            equipment_id=request.equipment_id,
            equipment_type=request.equipment_type,
            sensor_data=request.sensor_data
        )
        
        return AgentResponse(
            status="success",
            response=result.get("answer", "No anomalies detected"),
            metadata={
                "equipment_id": request.equipment_id,
                "risk_level": result.get("risk_level", "unknown"),
                "anomalies_detected": len(result.get("anomalies", [])),
                "agents_used": result.get("agents_used", [])
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anomaly check error: {str(e)}")


@router.get("/health")
async def agent_health():
    """Check if agent system is operational"""
    try:
        # Quick test - just import the modules
        from backend.src.agents import supervisor
        return {
            "status": "healthy",
            "agents": ["supervisor", "anomaly", "diagnosis", "recommendation", "report"],
            "graph_compiled": True
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Agent system unhealthy: {str(e)}")
