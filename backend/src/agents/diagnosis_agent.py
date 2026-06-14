"""
Diagnosis Agent — Root cause analysis and fault diagnosis
"""

import logging
import re
import json
from backend.src.agents.state import AgentState, RootCause
from backend.src.agents.tools import rag_retrieve
from backend.src.agents.prompts import (
    DIAGNOSIS_AGENT_PROMPT,
    format_sensor_readings,
    format_anomalies,
)
from backend.src.agents.llm_client import get_llm_client

logger = logging.getLogger(__name__)


def diagnosis_node(state: AgentState) -> AgentState:
    """
    Diagnosis Agent Node.
    
    Process:
    1. Build diagnostic query from symptoms
    2. Retrieve relevant failure patterns from RAG
    3. LLM performs root cause analysis
    4. Parse structured output
    5. Extract citations
    
    Updates state:
    - diagnosis
    - root_causes
    - risk_level (if not set)
    - rul_estimate
    - citations
    """
    logger.info("🔬 Diagnosis Agent executing...")
    
    state["completed_agents"].append("diagnosis")
    
    equipment_type = state.get("equipment_type", "Industrial Equipment")
    equipment_id = state.get("equipment_id", "Unknown")
    
    # Step 1: Build diagnostic query
    query_parts = [state["query"]]
    
    # Add anomaly info to query
    if state.get("anomalies_detected"):
        anomaly_types = [a.sensor_type for a in state["anomalies_detected"]]
        query_parts.append(f"{' '.join(set(anomaly_types))} anomaly")
    
    # Add error codes
    if state.get("error_codes"):
        query_parts.extend(state["error_codes"])
    
    diagnostic_query = f"{equipment_type} {' '.join(query_parts)} fault diagnosis root cause"
    
    # Step 2: Retrieve relevant documentation
    logger.info(f"Retrieving knowledge for: {diagnostic_query}")
    rag_result = rag_retrieve(diagnostic_query, top_k=5)
    
    if not rag_result.grounded:
        logger.warning("No relevant documentation found for diagnosis")
        state["diagnosis"] = "Insufficient information for diagnosis"
        state["errors"].append("No relevant documentation found")
        return state
    
    # Step 3: Format context for LLM
    llm = get_llm_client()
    
    prompt = DIAGNOSIS_AGENT_PROMPT.format(
        equipment_type=equipment_type,
        equipment_id=equipment_id,
        query=state["query"],
        sensor_readings=format_sensor_readings(state.get("sensor_readings", [])),
        anomalies=format_anomalies(state.get("anomalies_detected", [])),
        error_codes=", ".join(state.get("error_codes", [])) or "None",
        rag_context=rag_result.context,
    )
    
    # Step 4: LLM diagnosis
    try:
        diagnosis_output = llm.generate(prompt, max_tokens=600, temperature=0.2)
        
        # Step 5: Parse structured output
        parsed = _parse_diagnosis_output(diagnosis_output)
        
        state["diagnosis"] = parsed["diagnosis"]
        state["root_causes"] = parsed["root_causes"]
        
        # Set risk level if not already set
        if not state.get("risk_level"):
            state["risk_level"] = parsed["risk_level"]
        
        # RUL estimate
        if parsed["rul"]:
            state["rul_estimate"] = parsed["rul"]
        
        # Extract citations
        state["citations"].extend(_extract_citations(diagnosis_output, rag_result.sources))
        state["retrieved_chunks"].extend(rag_result.chunks)
        
        logger.info(f"✅ Diagnosis complete: {len(parsed['root_causes'])} root causes identified")
        
    except Exception as e:
        logger.error(f"Diagnosis LLM failed: {e}", exc_info=True)
        state["errors"].append(f"Diagnosis failed: {str(e)}")
        state["diagnosis"] = "Diagnosis failed due to processing error"
    
    return state


def _parse_diagnosis_output(text: str) -> dict:
    """Parse structured diagnosis output from LLM."""
    result = {
        "diagnosis": "",
        "root_causes": [],
        "risk_level": "MEDIUM",
        "rul": None,
    }
    
    # Extract primary diagnosis
    diagnosis_match = re.search(r"PRIMARY DIAGNOSIS:\s*(.+?)(?:\n\n|\n[A-Z])", text, re.DOTALL)
    if diagnosis_match:
        result["diagnosis"] = diagnosis_match.group(1).strip()
    
    # Extract root causes
    causes_section = re.search(r"ROOT CAUSES.*?:\s*(.+?)(?:\n\n[A-Z]|\nRISK LEVEL)", text, re.DOTALL)
    if causes_section:
        causes_text = causes_section.group(1)
        # Parse numbered causes
        for cause_match in re.finditer(r"(\d+)\.\s*(.+?)\s*\((?:Confidence|confidence):\s*(\d+)%\)", causes_text):
            cause_text = cause_match.group(2).strip()
            confidence = float(cause_match.group(3)) / 100
            
            # Extract evidence for this cause
            evidence = []
            evidence_section = causes_text[cause_match.end():].split("\n\n")[0]
            for evidence_line in re.findall(r"[-•]\s*(.+)", evidence_section):
                evidence.append(evidence_line.strip())
            
            result["root_causes"].append(RootCause(
                cause=cause_text,
                confidence=confidence,
                evidence=evidence[:3],  # Top 3 evidence points
                doc_sources=[],
            ))
    
    # Extract risk level
    risk_match = re.search(r"RISK LEVEL:\s*(CRITICAL|HIGH|MEDIUM|LOW)", text, re.IGNORECASE)
    if risk_match:
        result["risk_level"] = risk_match.group(1).upper()
    
    # Extract RUL
    rul_match = re.search(r"REMAINING USEFUL LIFE:\s*(.+?)(?:\n\n|\n[A-Z])", text, re.DOTALL)
    if rul_match:
        rul_text = rul_match.group(1).strip()
        # Try to extract hours/days
        hours_match = re.search(r"(\d+)\s*(?:hours?|hrs?)", rul_text, re.IGNORECASE)
        days_match = re.search(r"(\d+)\s*days?", rul_text, re.IGNORECASE)
        
        if hours_match or days_match:
            result["rul"] = {
                "estimate": rul_text,
                "hours": int(hours_match.group(1)) if hours_match else None,
                "days": int(days_match.group(1)) if days_match else None,
            }
    
    return result


def _extract_citations(text: str, sources: list[dict]) -> list[dict]:
    """Extract citation markers [1], [2] and match to sources."""
    citations = []
    
    # Find all [N] markers
    citation_markers = re.findall(r"\[(\d+)\]", text)
    
    for marker in set(citation_markers):
        idx = int(marker) - 1  # Convert to 0-indexed
        if 0 <= idx < len(sources):
            source = sources[idx]
            citations.append({
                "index": int(marker),
                "doc_name": source.get("doc_name", ""),
                "section": source.get("section", ""),
                "pages": source.get("pages", []),
                "bboxes": source.get("bboxes", []), #bbox for bounding the pdf 
            })
    
    return citations
