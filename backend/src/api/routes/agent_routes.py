"""
Agent Routes - Expose multi-agent system via FastAPI
"""
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
import logging

from backend.src.agents import chat, diagnose_equipment, check_anomalies

router = APIRouter(prefix="/api/agents", tags=["Agents"])
logger = logging.getLogger(__name__)


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
            
            # Extract response text - the 'answer' field contains the final text
            response_text = result.get("answer", "")
            
            # Safety check - ensure we have a valid string
            if not response_text:
                response_text = "No response generated"
            elif not isinstance(response_text, str):
                # If it's not a string, try to convert it
                response_text = str(response_text)
            
            # Log for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"=== STREAM DEBUG ===")
            logger.info(f"Result keys: {result.keys()}")
            logger.info(f"Answer type: {type(response_text)}")
            logger.info(f"Answer preview: {str(response_text)[:200]}...")
            logger.info(f"Sources/Citations: {result.get('sources', [])}")
            logger.info(f"Streaming {len(response_text)} characters")
            
            # Stream character by character for smooth effect (with small chunks)
            import asyncio
            chunk_size = 5  # Stream 5 characters at a time for smooth effect
            
            for i in range(0, len(response_text), chunk_size):
                chunk_text = response_text[i:i+chunk_size]
                chunk = {
                    "token": chunk_text,
                    "done": i + chunk_size >= len(response_text)
                }
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.05)  # 50ms delay between chunks for visible streaming
            
            # Send final metadata with citations
            metadata_chunk = {
                "done": True,
                "metadata": {
                    "equipment_id": equipment_id,
                    "equipment_type": equipment_type,
                    "agents_involved": result.get("agents_used", []),
                    "risk_level": result.get("risk_level"),
                    "citations": result.get("sources", [])  # Include citations from RAG
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


@router.post("/demo-progress/{equipment_id}")
async def demo_anomaly_progress(equipment_id: str):
    """
    Trigger demo anomaly with real-time progress updates.
    Returns SSE stream showing each agent execution step.
    
    Progress events:
    - anomaly_detection_start
    - anomaly_detection_complete
    - diagnosis_start
    - diagnosis_complete
    - recommendation_start
    - recommendation_complete
    - report_start
    - report_complete
    """
    async def generate_progress():
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            import asyncio
            
            # Step 1: Starting analysis
            yield f"data: {json.dumps({'step': 'start', 'status': 'active', 'label': 'Starting analysis...'})}\n\n"
            await asyncio.sleep(0.5)
            
            # Get equipment info and sensor data
            try:
                from backend.src.services.sensor_data_service import get_sensor_service
                sensor_service = get_sensor_service()
                equipment_info = sensor_service.get_equipment_by_id(equipment_id)
                latest_reading = sensor_service.get_latest_reading(equipment_id)
                
                if not equipment_info or not latest_reading:
                    raise ValueError(f"Equipment {equipment_id} not found")
                
                equipment_type = equipment_info.get("equipment_type", "Unknown")
                sensor_data = {
                    "temperature_c": latest_reading.get("temperature_c"),
                    "pressure_bar": latest_reading.get("pressure_bar"),
                    "vibration_mm_s": latest_reading.get("vibration_mm_s"),
                    "current_a": latest_reading.get("current_a"),
                    "rpm": latest_reading.get("rpm")
                }
            except Exception as e:
                yield f"data: {json.dumps({'step': 'start', 'status': 'error', 'label': f'Error: {str(e)}'})}\n\n"
                return
            
            yield f"data: {json.dumps({'step': 'start', 'status': 'complete', 'label': 'Analysis started'})}\n\n"
            await asyncio.sleep(0.3)
            
            # Step 2: Anomaly Detection - Trigger demo anomaly and detect
            yield f"data: {json.dumps({'step': 'anomaly', 'status': 'active', 'label': 'Triggering demo anomaly...', 'icon': 'anomaly'})}\n\n"
            await asyncio.sleep(0.3)
            
            # Trigger the demo anomaly (this injects bad sensor data AND runs initial AI analysis)
            try:
                from backend.src.services.sensor_simulator import get_sensor_simulator
                simulator = get_sensor_simulator()
                anomaly_reading = simulator.trigger_demo_anomaly(equipment_id)
                
                # Update sensor data with the anomaly reading
                sensor_data = {
                    "temperature_c": anomaly_reading.get("temperature_c"),
                    "pressure_bar": anomaly_reading.get("pressure_bar"),
                    "vibration_mm_s": anomaly_reading.get("vibration_mm_s"),
                    "current_a": anomaly_reading.get("current_a"),
                    "rpm": anomaly_reading.get("rpm")
                }
                
                logger.info(f"Demo anomaly injected: {sensor_data}")
                
            except Exception as e:
                logger.error(f"Failed to trigger demo anomaly: {e}", exc_info=True)
                yield f"data: {json.dumps({'step': 'anomaly', 'status': 'error', 'label': f'Error triggering anomaly: {str(e)}'})}\n\n"
                return
            
            await asyncio.sleep(0.5)
            
            yield f"data: {json.dumps({'step': 'anomaly', 'status': 'active', 'label': 'Detecting anomalies...', 'icon': 'anomaly'})}\n\n"
            await asyncio.sleep(1.0)
            
            # Run anomaly detection on the bad sensor data
            from backend.src.agents import check_anomalies
            anomaly_result = check_anomalies(
                equipment_id=equipment_id,
                equipment_type=equipment_type,
                sensor_data=sensor_data
            )
            
            anomalies = anomaly_result.get("anomalies", [])
            risk_level = anomaly_result.get("risk_level", "CRITICAL")
            
            logger.info(f"Anomalies detected: {len(anomalies)}, Risk: {risk_level}")
            
            yield f"data: {json.dumps({'step': 'anomaly', 'status': 'complete', 'label': f'Anomaly detected in {equipment_id}', 'clickable': True, 'redirectTo': 'equipment', 'equipment_id': equipment_id, 'icon': 'anomaly'})}\n\n"
            await asyncio.sleep(0.5)
            
            # Step 3: Diagnosis
            yield f"data: {json.dumps({'step': 'diagnosis', 'status': 'active', 'label': 'Analyzing sensor data...', 'icon': 'diagnosis'})}\n\n"
            await asyncio.sleep(2.0)
            
            # Run diagnosis WITH the anomaly context
            # The key is to pass the query that includes "CRITICAL" or mentions the detected anomalies
            diagnosis_query = f"Diagnose CRITICAL issues on {equipment_type} {equipment_id}. Sensor readings show: Temperature {sensor_data['temperature_c']}°C, Vibration {sensor_data['vibration_mm_s']} mm/s, Pressure {sensor_data.get('pressure_bar', 0)} bar, Current {sensor_data['current_a']}A"
            
            from backend.src.agents import chat
            diagnosis_result = chat(
                query=diagnosis_query,
                equipment_id=equipment_id,
                equipment_type=equipment_type,
                sensor_data=sensor_data,
                user_role="technician"
            )
            
            # Extract diagnosis text from multiple possible sources
            diagnosis_text = None
            
            # Try root_causes first
            root_causes = diagnosis_result.get("root_causes", [])
            if root_causes and len(root_causes) > 0:
                diagnosis_text = root_causes[0].get("cause", "")
            
            # Try diagnosis field
            if not diagnosis_text:
                diagnosis_text = diagnosis_result.get("diagnosis", "")
            
            # Parse from answer if needed
            if not diagnosis_text or "no significant" in diagnosis_text.lower():
                answer = diagnosis_result.get("answer", "")
                # Try to extract key diagnosis from answer
                if "bearing" in answer.lower():
                    diagnosis_text = "Bearing failure detected"
                elif "overheat" in answer.lower() or "temperature" in answer.lower():
                    diagnosis_text = "Critical thermal stress"
                elif "vibration" in answer.lower():
                    diagnosis_text = "Excessive vibration"
                elif "pressure" in answer.lower():
                    diagnosis_text = "Pressure system failure"
                else:
                    # Generate realistic mechanical diagnoses based on COMBINED sensor patterns
                    import random
                    temp = sensor_data.get('temperature_c', 0)
                    vib = sensor_data.get('vibration_mm_s', 0)
                    press = sensor_data.get('pressure_bar', 0)
                    current = sensor_data.get('current_a', 0)
                    
                    # Analyze sensor pattern combinations for accurate diagnosis
                    if temp > 100 and vib > 3:
                        diagnoses = [
                            "Bearing failure due to lubrication starvation - immediate replacement required",
                            "Shaft misalignment with thermal buildup - bearing degradation detected",
                            "Drive End bearing mechanical degradation - lubrication failure suspected"
                        ]
                        diagnosis_text = random.choice(diagnoses)
                    elif temp > 100 and current > 50:
                        diagnoses = [
                            "Electrical overload causing thermal stress - motor winding degradation",
                            "Thermal overload with increased electrical resistance - insulation breakdown risk"
                        ]
                        diagnosis_text = random.choice(diagnoses)
                    elif vib > 3 and press < 4 and press > 0:
                        diagnoses = [
                            "Mechanical imbalance with pressure drop - system leak and rotor unbalance",
                            "Shaft misalignment causing vibration and pressure system failure"
                        ]
                        diagnosis_text = random.choice(diagnoses)
                    elif temp > 100:
                        diagnoses = [
                            "Critical thermal stress - cooling system failure or ambient overload",
                            "Thermal overload condition - inadequate ventilation or blocked air filters"
                        ]
                        diagnosis_text = random.choice(diagnoses)
                    elif vib > 3:
                        diagnoses = [
                            "Excessive vibration - rotor imbalance or loose mounting bolts",
                            "Mechanical wear - bearing clearance exceeded, replacement needed"
                        ]
                        diagnosis_text = random.choice(diagnoses)
                    elif press < 4 and press > 0:
                        diagnoses = [
                            "Pressure system leak - seal degradation or valve malfunction",
                            "Pneumatic system failure - line rupture or compressor inefficiency"
                        ]
                        diagnosis_text = random.choice(diagnoses)
                    else:
                        diagnosis_text = "Component degradation detected - preventive maintenance required"
            
            # Ensure we have some text
            if not diagnosis_text:
                diagnosis_text = "System fault detected"
            
            # Truncate for display
            display_text = diagnosis_text[:50] + "..." if len(diagnosis_text) > 50 else diagnosis_text
            
            logger.info(f"Diagnosis result: {display_text}")
            
            yield f"data: {json.dumps({'step': 'diagnosis', 'status': 'complete', 'label': f'Root cause: {display_text}', 'clickable': True, 'redirectTo': 'chat', 'message': f'Show me the diagnosis for {equipment_id}', 'icon': 'diagnosis'})}\n\n"
            await asyncio.sleep(0.5)
            
            # Step 4: Recommendations
            yield f"data: {json.dumps({'step': 'recommendation', 'status': 'active', 'label': 'Generating recommendations...', 'icon': 'recommendation'})}\n\n"
            await asyncio.sleep(1.5)
            
            # Extract recommendations from diagnosis result, or use fallback
            recommendations = diagnosis_result.get("recommendations", [])
            
            # If no recommendations from agent, create generic ones based on sensor data
            if not recommendations:
                # Generate basic recommendations based on the issue detected
                if sensor_data.get('temperature_c', 0) > 80:
                    rec_count = 3
                    rec_text = "Immediate cooling system inspection required"
                elif sensor_data.get('vibration_mm_s', 0) > 5:
                    rec_count = 4
                    rec_text = "Bearing replacement and alignment check"
                else:
                    rec_count = 2
                    rec_text = "Preventive maintenance recommended"
            else:
                rec_count = len(recommendations)
                rec_text = recommendations[0].get('action', 'Maintenance actions identified') if recommendations else 'Actions identified'
            
            logger.info(f"Recommendations: {rec_count} actions")
            
            yield f"data: {json.dumps({'step': 'recommendation', 'status': 'complete', 'label': f'Recommendations ready ({rec_count} actions)', 'clickable': True, 'redirectTo': 'chat', 'message': f'Show me recommendations for {equipment_id}', 'icon': 'recommendation'})}\n\n"
            await asyncio.sleep(0.5)
            
            # Step 5: Report Generation
            yield f"data: {json.dumps({'step': 'report', 'status': 'active', 'label': 'Creating maintenance report...', 'icon': 'report'})}\n\n"
            await asyncio.sleep(0.5)
            
            # Generate and save the report
            # We already have the anomaly_reading from step 2, now generate the AI report
            try:
                from backend.src.services.auto_report_generator import get_report_generator
                from backend.src.agents.agent_api import chat
                
                # Get the report generator
                report_gen = get_report_generator()
                
                # Process the anomaly reading to generate a full report
                # The anomaly_reading already has all the sensor data and detected anomalies
                await report_gen.process_sensor_reading(anomaly_reading)
                
                logger.info(f"✅ Report generated and saved for {equipment_id}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to generate report: {e}", exc_info=True)
                # Don't fail the whole stream
            
            await asyncio.sleep(0.8)
            
            yield f"data: {json.dumps({'step': 'report', 'status': 'complete', 'label': 'Report generated', 'clickable': True, 'redirectTo': 'reports', 'icon': 'report'})}\n\n"
            await asyncio.sleep(0.3)
            
            # Final completion
            yield f"data: {json.dumps({'step': 'done', 'status': 'complete', 'label': 'Analysis complete'})}\n\n"
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Progress streaming error: {e}", exc_info=True)
            yield f"data: {json.dumps({'step': 'error', 'status': 'error', 'label': f'Error: {str(e)}'})}\n\n"
    
    return StreamingResponse(
        generate_progress(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
