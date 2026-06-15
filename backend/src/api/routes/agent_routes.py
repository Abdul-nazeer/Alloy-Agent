"""
Agent Routes - Expose multi-agent system via FastAPI
"""
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
import json

from backend.src.agents import chat, diagnose_equipment, check_anomalies

router = APIRouter(prefix="/api/agents", tags=["Agents"])


# ══════════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ══════════════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    """Chat with the multi-agent system"""
    message: str = Field(..., description="User message or question")
    session_id: Optional[str] = Field("default", description="Conversation session ID for memory")
    equipment_id: Optional[str] = Field(None, description="Equipment ID (optional, will be extracted from message if not provided)")
    sensor_data: Optional[Dict[str, float]] = Field(None, description="Current sensor readings (optional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What's causing the temperature spike on AC-001?",
                "session_id": "session_123",
                "equipment_id": "AC-001",
                "sensor_data": {
                    "temperature_c": 95.5,
                    "pressure_bar": 5.2,
                    "vibration_mm_s": 8.1,
                    "current_a": 45.3,
                    "rpm": 1450
                }
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
    
    Equipment context can be provided via:
    1. Explicit equipment_id and sensor_data parameters
    2. Automatic extraction from message (e.g., "AC-001", "Air Compressor")
    """
    try:
        # Extract equipment context from message if not provided
        equipment_id = request.equipment_id
        equipment_type = None
        sensor_data = request.sensor_data
        
        # Try to extract equipment ID from message if not provided
        if not equipment_id:
            import re
            # Match patterns like AC-001, CF-003, RM-005, etc.
            equipment_pattern = r'\b([A-Z]{2}-\d{3})\b'
            match = re.search(equipment_pattern, request.message)
            if match:
                equipment_id = match.group(1)
        
        # Determine equipment type from ID or fetch from database
        if equipment_id:
            # Get equipment type from sensor service
            try:
                from backend.src.services.sensor_data_service import get_sensor_service
                sensor_service = get_sensor_service()
                equipment_info = sensor_service.get_equipment_by_id(equipment_id)
                if equipment_info:
                    equipment_type = equipment_info.get("equipment_type")
                    
                    # If no sensor data provided, fetch latest readings
                    if not sensor_data:
                        latest = sensor_service.get_latest_reading(equipment_id)
                        if latest:
                            sensor_data = {
                                "temperature_c": latest.get("temperature_c"),
                                "pressure_bar": latest.get("pressure_bar"),
                                "vibration_mm_s": latest.get("vibration_mm_s"),
                                "current_a": latest.get("current_a"),
                                "rpm": latest.get("rpm")
                            }
            except Exception as e:
                pass  # Continue without equipment context
        
        # Call agent with enriched context
        result = chat(
            query=request.message,
            equipment_id=equipment_id,
            equipment_type=equipment_type,
            sensor_data=sensor_data,
            session_id=request.session_id or "default"
        )
        
        # Extract the answer text from agent response
        answer_text = result.get("answer", "No response generated")
        
        return AgentResponse(
            status="success",
            response=answer_text,  # Main response field
            metadata={
                "equipment_id": equipment_id,
                "equipment_type": equipment_type,
                "agents_involved": result.get("agents_used", []),
                "risk_level": result.get("risk_level"),
                "sources_count": len(result.get("sources", [])),
                "anomalies_count": len(result.get("anomalies", [])),
                "recommendations_count": len(result.get("recommendations", [])),
                "citations": result.get("sources", [])  # Include citations in metadata
            },
            session_id=request.session_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@router.post("/chat/stream")
async def agent_chat_stream(request: ChatRequest):
    """
    Chat with streaming response (Server-Sent Events)
    
    Response arrives token-by-token for better UX.
    Compatible with all agent types (conversational, diagnosis, etc.)
    """
    async def generate_stream():
        try:
            # Extract equipment context
            equipment_id = request.equipment_id
            equipment_type = None
            sensor_data = request.sensor_data
            
            # Try to extract equipment ID from message if not provided
            if not equipment_id:
                import re
                equipment_pattern = r'\b([A-Z]{2}-\d{3})\b'
                match = re.search(equipment_pattern, request.message)
                if match:
                    equipment_id = match.group(1)
            
            # Get equipment context
            if equipment_id:
                try:
                    from backend.src.services.sensor_data_service import get_sensor_service
                    sensor_service = get_sensor_service()
                    equipment_info = sensor_service.get_equipment_by_id(equipment_id)
                    if equipment_info:
                        equipment_type = equipment_info.get("equipment_type")
                        if not sensor_data:
                            latest = sensor_service.get_latest_reading(equipment_id)
                            if latest:
                                sensor_data = {
                                    "temperature_c": latest.get("temperature_c"),
                                    "pressure_bar": latest.get("pressure_bar"),
                                    "vibration_mm_s": latest.get("vibration_mm_s"),
                                    "current_a": latest.get("current_a"),
                                    "rpm": latest.get("rpm")
                                }
                except Exception as e:
                    pass
            
            # Call agent (this still returns full response, but we'll stream it)
            result = chat(
                query=request.message,
                equipment_id=equipment_id,
                equipment_type=equipment_type,
                sensor_data=sensor_data,
                session_id=request.session_id or "default"
            )
            
            response_text = result.get("answer", "No response generated")
            
            # Stream the response word by word
            words = response_text.split()
            for i, word in enumerate(words):
                chunk = {
                    "token": word + (" " if i < len(words) - 1 else ""),
                    "done": i == len(words) - 1
                }
                yield f"data: {json.dumps(chunk)}\n\n"
            
            # Send final metadata
            metadata_chunk = {
                "done": True,
                "metadata": {
                    "equipment_id": equipment_id,
                    "equipment_type": equipment_type,
                    "agents_involved": result.get("agents_used", []),
                    "risk_level": result.get("risk_level"),
                }
            }
            yield f"data: {json.dumps(metadata_chunk)}\n\n"
            
        except Exception as e:
            error_chunk = {
                "error": str(e),
                "done": True
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


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
        from backend.src.agents.llm_client import get_llm_client
        from backend.src.rag.config import LLM_PROVIDER, HF_MODEL_ID
        
        # Get LLM client info
        llm_client = get_llm_client()
        
        return {
            "status": "healthy",
            "agents": ["supervisor", "anomaly", "diagnosis", "recommendation", "report"],
            "graph_compiled": True,
            "llm_provider": LLM_PROVIDER,
            "llm_model": HF_MODEL_ID if LLM_PROVIDER == "huggingface" else "unknown"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Agent system unhealthy: {str(e)}")


@router.get("/rag/status")
async def rag_status():
    """Check RAG system status and knowledge base"""
    try:
        from backend.src.rag.retriever import search_documents
        from backend.src.rag.config import COLLECTION_CHUNKS, QDRANT_URL
        
        # Try a test query
        test_results = search_documents("maintenance", top_k=3)
        
        return {
            "status": "operational" if test_results else "no_data",
            "qdrant_url": QDRANT_URL,
            "collection": COLLECTION_CHUNKS,
            "test_query_results": len(test_results),
            "knowledge_base_populated": len(test_results) > 0
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "knowledge_base_populated": False
        }
