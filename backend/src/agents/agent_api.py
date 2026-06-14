"""
Agent API — High-level interface for the multi-agent system

Provides simple chat() function that handles the entire agent workflow.
"""

import logging
from typing import Optional, Dict, Any
from backend.src.agents.state import create_initial_state, parse_sensor_readings
from backend.src.agents.supervisor import run_agent_graph

logger = logging.getLogger(__name__)


def chat(
    query: str,
    equipment_id: Optional[str] = None,
    equipment_type: Optional[str] = None,
    sensor_data: Optional[Dict[str, Any]] = None,
    error_codes: Optional[list[str]] = None,
    user_role: str = "technician",
    session_id: str = "default",
    uploaded_doc_ids: Optional[list[str]] = None,
) -> Dict[str, Any]:
    """
    Main entry point for multi-agent chat.
    
    Args:
        query: User's natural language question
        equipment_id: Equipment identifier (e.g., "FC-TH-01")
        equipment_type: Equipment type (e.g., "Air Compressor")
        sensor_data: Dict of sensor readings {sensor_type: value} or {sensor_type: {value, unit, timestamp}}
        error_codes: List of equipment error codes
        user_role: "technician" | "supervisor" | "manager" (controls output depth)
        session_id: Session ID for multi-turn conversations
        uploaded_doc_ids: User-uploaded document IDs to include in RAG search
    
    Returns:
        Response dict with:
        - answer: Final answer text
        - report: Full structured report (if generated)
        - sources: List of source citations
        - risk_level: CRITICAL | HIGH | MEDIUM | LOW
        - recommendations: List of action recommendations
        - diagnosis: Fault diagnosis (if performed)
        - metadata: Additional info (cost, downtime, etc.)
        - agents_used: List of agents that executed
        - errors: Any errors encountered
    
    Example:
        >>> response = chat(
        ...     query="Diagnose air compressor AC-001",
        ...     equipment_id="AC-001",
        ...     equipment_type="Air Compressor",
        ...     sensor_data={"TEMP": 112.5, "VIB": 3.2, "PRES": 1.61},
        ...     user_role="technician"
        ... )
        >>> print(response["answer"])
    """
    logger.info(f"=== Agent Chat Request ===")
    logger.info(f"Query: {query}")
    logger.info(f"Equipment: {equipment_type} ({equipment_id})")
    logger.info(f"Session: {session_id}")
    
    # Parse sensor data
    sensor_readings = []
    if sensor_data:
        sensor_readings = parse_sensor_readings(sensor_data)
        logger.info(f"Sensor readings: {len(sensor_readings)} sensors")
    
    # Create initial state
    state = create_initial_state(
        query=query,
        equipment_id=equipment_id,
        equipment_type=equipment_type,
        sensor_readings=sensor_readings,
        error_codes=error_codes,
        user_role=user_role,
        session_id=session_id,
        uploaded_doc_ids=uploaded_doc_ids,
    )
    
    # Run the agent graph
    final_state = run_agent_graph(state, session_id=session_id)
    
    # Format response
    response = {
        "answer": final_state.get("final_answer", "No response generated"),
        "report": final_state.get("report_content"),
        "sources": _format_sources(final_state.get("citations", [])),
        "risk_level": final_state.get("risk_level"),
        "recommendations": [
            {
                "priority": rec.priority,
                "action": rec.action,
                "reason": rec.reason,
                "estimated_time": rec.estimated_time,
                "required_parts": rec.required_parts,
                "safety_notes": rec.safety_notes,
            }
            for rec in final_state.get("recommendations", [])
        ],
        "diagnosis": final_state.get("diagnosis"),
        "root_causes": [
            {
                "cause": rc.cause,
                "confidence": rc.confidence,
                "evidence": rc.evidence,
            }
            for rc in final_state.get("root_causes", [])
        ],
        "anomalies": [
            {
                "sensor": a.sensor_type,
                "value": a.current_value,
                "threshold": a.threshold,
                "deviation_percent": a.deviation_percent,
                "severity": a.severity,
                "message": a.message,
            }
            for a in final_state.get("anomalies_detected", [])
        ],
        "rul_estimate": final_state.get("rul_estimate"),
        "metadata": final_state.get("metadata", {}),
        "agents_used": final_state.get("completed_agents", []),
        "errors": final_state.get("errors", []),
        "session_id": session_id,
    }
    
    logger.info(f"=== Agent Response ===")
    logger.info(f"Risk: {response['risk_level']}")
    logger.info(f"Agents used: {response['agents_used']}")
    logger.info(f"Sources: {len(response['sources'])}")
    
    return response


def _format_sources(citations: list[dict]) -> list[dict]:
    """Format citations into source list for frontend."""
    sources = []
    
    for citation in citations:
        sources.append({
            "index": citation.get("index"),
            "document": citation.get("doc_name"),
            "section": citation.get("section"),
            "pages": citation.get("pages", []),
            "bboxes": citation.get("bboxes", []),
        })
    
    return sources


# ══════════════════════════════════════════════════════════════════════════════
# Convenience Functions
# ══════════════════════════════════════════════════════════════════════════════

def diagnose_equipment(
    equipment_id: str,
    equipment_type: str,
    sensor_data: Dict[str, Any],
    error_codes: Optional[list[str]] = None,
    user_role: str = "technician",
) -> Dict[str, Any]:
    """
    Convenience function for equipment diagnosis.
    
    Automatically generates appropriate query and runs full diagnosis flow.
    """
    query = f"Diagnose {equipment_type} {equipment_id}"
    
    if error_codes:
        query += f" showing error codes: {', '.join(error_codes)}"
    
    return chat(
        query=query,
        equipment_id=equipment_id,
        equipment_type=equipment_type,
        sensor_data=sensor_data,
        error_codes=error_codes,
        user_role=user_role,
    )


def generate_maintenance_report(
    equipment_id: str,
    equipment_type: str,
    findings: str,
    user_role: str = "supervisor",
) -> Dict[str, Any]:
    """
    Convenience function to generate a maintenance report from findings.
    """
    query = f"Generate maintenance report for {equipment_type} {equipment_id}: {findings}"
    
    return chat(
        query=query,
        equipment_id=equipment_id,
        equipment_type=equipment_type,
        user_role=user_role,
    )


def check_anomalies(
    equipment_id: str,
    equipment_type: str,
    sensor_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convenience function for real-time anomaly detection.
    """
    query = f"Check sensor readings for anomalies on {equipment_type} {equipment_id}"
    
    return chat(
        query=query,
        equipment_id=equipment_id,
        equipment_type=equipment_type,
        sensor_data=sensor_data,
        user_role="technician",
    )
