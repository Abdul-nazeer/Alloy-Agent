"""
Anomaly Detection Agent — Real-time sensor analysis and threshold violation detection
"""

import logging
from typing import Optional
from backend.src.agents.state import AgentState, Anomaly
from backend.src.agents.tools import rag_retrieve, threshold_lookup
from backend.src.agents.prompts import (
    ANOMALY_DETECTION_PROMPT,
    format_sensor_readings,
    format_thresholds,
)
from backend.src.agents.llm_client import get_llm_client

logger = logging.getLogger(__name__)


def anomaly_detection_node(state: AgentState) -> AgentState:
    """
    Anomaly Detection Agent Node.
    
    Process:
    1. Compare sensor readings against thresholds
    2. Identify violations and patterns
    3. Classify severity
    4. Retrieve relevant documentation
    5. Generate analysis with LLM
    
    Updates state:
    - anomalies_detected
    - risk_level
    - requires_escalation
    - retrieved_chunks
    """
    logger.info("🔍 Anomaly Detection Agent executing...")
    
    state["completed_agents"].append("anomaly")
    
    # Check if we have sensor data
    if not state.get("sensor_readings"):
        logger.warning("No sensor readings provided")
        state["errors"].append("Anomaly agent requires sensor readings")
        state["anomalies_detected"] = []
        state["risk_level"] = "LOW"
        return state
    
    equipment_type = state.get("equipment_type", "General Industrial Motor")
    sensor_readings = state["sensor_readings"]
    
    # Step 1: Threshold comparison
    anomalies = []
    thresholds_info = []
    
    for reading in sensor_readings:
        threshold = threshold_lookup(equipment_type, reading.sensor_type)
        
        if threshold:
            thresholds_info.append(threshold)
            
            # Check if exceeds critical threshold
            if reading.value > threshold.critical_threshold:
                deviation = ((reading.value - threshold.critical_threshold) / threshold.critical_threshold) * 100
                anomaly = Anomaly(
                    sensor_type=reading.sensor_type,
                    current_value=reading.value,
                    threshold=threshold.critical_threshold,
                    deviation_percent=deviation,
                    severity="CRITICAL",
                    message=f"{reading.sensor_type} critically high: {reading.value}{threshold.unit} (>{threshold.critical_threshold}{threshold.unit})"
                )
                anomalies.append(anomaly)
                reading.is_anomalous = True
                reading.severity = "CRITICAL"
                
            # Check if exceeds warning threshold
            elif reading.value > threshold.warning_threshold:
                deviation = ((reading.value - threshold.warning_threshold) / threshold.warning_threshold) * 100
                anomaly = Anomaly(
                    sensor_type=reading.sensor_type,
                    current_value=reading.value,
                    threshold=threshold.warning_threshold,
                    deviation_percent=deviation,
                    severity="HIGH",
                    message=f"{reading.sensor_type} above warning: {reading.value}{threshold.unit} (>{threshold.warning_threshold}{threshold.unit})"
                )
                anomalies.append(anomaly)
                reading.is_anomalous = True
                reading.severity = "HIGH"
            
            # Check if below minimum (for pressure, etc.)
            elif reading.value < threshold.normal_min:
                deviation = ((threshold.normal_min - reading.value) / threshold.normal_min) * 100
                anomaly = Anomaly(
                    sensor_type=reading.sensor_type,
                    current_value=reading.value,
                    threshold=threshold.normal_min,
                    deviation_percent=deviation,
                    severity="MEDIUM",
                    message=f"{reading.sensor_type} below normal: {reading.value}{threshold.unit} (<{threshold.normal_min}{threshold.unit})"
                )
                anomalies.append(anomaly)
                reading.is_anomalous = True
                reading.severity = "MEDIUM"
    
    # Step 2: Determine overall risk level
    if any(a.severity == "CRITICAL" for a in anomalies):
        risk_level = "CRITICAL"
        requires_escalation = True
    elif any(a.severity == "HIGH" for a in anomalies):
        risk_level = "HIGH"
        requires_escalation = True
    elif any(a.severity == "MEDIUM" for a in anomalies):
        risk_level = "MEDIUM"
        requires_escalation = False
    else:
        risk_level = "LOW"
        requires_escalation = False
    
    # Step 3: Retrieve relevant documentation
    if anomalies:
        # Build query from detected anomalies
        anomaly_types = " ".join(set(a.sensor_type for a in anomalies))
        rag_query = f"{equipment_type} {anomaly_types} threshold alarm troubleshooting"
        
        rag_result = rag_retrieve(rag_query, top_k=3)
        rag_context = rag_result.context if rag_result.grounded else "No relevant documentation found."
        retrieved_chunks = rag_result.chunks
    else:
        rag_context = "All readings normal."
        retrieved_chunks = []
    
    # Step 4: LLM analysis (multi-variate pattern detection)
    try:
        llm = get_llm_client()
        
        prompt = ANOMALY_DETECTION_PROMPT.format(
            equipment_type=equipment_type,
            equipment_id=state.get("equipment_id", "Unknown"),
            sensor_readings=format_sensor_readings(sensor_readings),
            thresholds=format_thresholds(thresholds_info),
            rag_context=rag_context,
        )
        
        llm_analysis = llm.generate(prompt, max_tokens=300, temperature=0.2)
        
        # Append LLM insights to metadata
        state["metadata"]["anomaly_analysis"] = llm_analysis
        
    except Exception as e:
        logger.error(f"LLM analysis failed: {e}")
        state["errors"].append(f"Anomaly LLM analysis failed: {str(e)}")
    
    # Step 5: Update state
    state["anomalies_detected"] = anomalies
    state["risk_level"] = risk_level
    state["requires_escalation"] = requires_escalation
    state["retrieved_chunks"].extend(retrieved_chunks)
    
    logger.info(f"✅ Anomaly Detection complete: {len(anomalies)} anomalies, risk={risk_level}")
    
    # Auto-escalate if CRITICAL
    if requires_escalation:
        from backend.src.agents.tools import escalation_notify
        escalation_notify(
            equipment_id=state.get("equipment_id", "Unknown"),
            severity=risk_level,
            message=f"{len(anomalies)} critical anomalies detected",
            recipient_role="supervisor"
        )
    
    return state
