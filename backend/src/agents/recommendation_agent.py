"""
Recommendation Agent — Action planning and maintenance procedures
"""

import logging
import re
from backend.src.agents.state import AgentState, Recommendation
from backend.src.agents.tools import rag_retrieve, spare_parts_lookup
from backend.src.agents.prompts import (
    RECOMMENDATION_AGENT_PROMPT,
    format_root_causes,
)
from backend.src.agents.llm_client import get_llm_client

logger = logging.getLogger(__name__)


def recommendation_node(state: AgentState) -> AgentState:
    """
    Recommendation Agent Node.
    
    Process:
    1. Retrieve maintenance procedures from RAG
    2. Check spare parts availability
    3. Generate role-specific recommendations
    4. Parse structured output
    5. Prioritize actions
    
    Updates state:
    - recommendations
    - metadata (downtime, cost estimates)
    """
    logger.info("📋 Recommendation Agent executing...")
    
    state["completed_agents"].append("recommendation")
    
    equipment_type = state.get("equipment_type", "Industrial Equipment")
    equipment_id = state.get("equipment_id", "Unknown")
    diagnosis = state.get("diagnosis", "No diagnosis available")
    root_causes = state.get("root_causes", [])
    risk_level = state.get("risk_level", "MEDIUM")
    user_role = state.get("user_role", "technician")
    
    # Step 1: Retrieve maintenance procedures
    # Build query from diagnosis and root causes
    if root_causes:
        primary_cause = root_causes[0].cause if root_causes else ""
        procedure_query = f"{equipment_type} {primary_cause} repair procedure maintenance steps"
    else:
        procedure_query = f"{equipment_type} {state['query']} maintenance procedure"
    
    logger.info(f"Retrieving procedures for: {procedure_query}")
    rag_result = rag_retrieve(procedure_query, top_k=5)
    
    # Step 2: Lookup spare parts availability from database
    from backend.src.agents.tools import get_critical_spare_parts
    
    spare_parts_info = []
    
    # Get all parts for this equipment type
    all_parts = spare_parts_lookup(equipment_type=equipment_type)
    
    # Get critical/out-of-stock parts
    critical_parts = get_critical_spare_parts(equipment_type)
    
    # Try to identify specific required parts from root causes
    part_keywords = _identify_parts(root_causes, diagnosis)
    
    if part_keywords:
        for keyword in part_keywords:
            matching_parts = spare_parts_lookup(equipment_type=equipment_type, part_keyword=keyword)
            spare_parts_info.extend(matching_parts)
    
    # If no specific parts identified, show critical parts that need attention
    if not spare_parts_info and critical_parts:
        spare_parts_info = critical_parts[:3]  # Top 3 critical parts
    
    # Format spare parts for prompt
    if spare_parts_info:
        spare_parts_text = "\n".join([
            f"- {p['part_number']}: {p['description']} | "
            f"Status: {p['status']} ({p['in_stock']} in stock) | "
            f"Lead time: {p['lead_time_days']} days | "
            f"Cost: ${p['cost']:.2f} | "
            f"Criticality: {p['criticality']} | "
            f"Supplier: {p['supplier']}"
            for p in spare_parts_info
        ])
    else:
        spare_parts_text = "No critical spare parts identified for this equipment type."
    
    # Add RUL prediction if available
    rul_info = state.get("metadata", {}).get("remaining_useful_life", {})
    if rul_info:
        rul_text = f"\n\nREMAINING USEFUL LIFE PREDICTION:\n{rul_info.get('message', 'N/A')}"
        rul_text += f"\nEstimated days remaining: {rul_info.get('estimated_days_remaining', 'Unknown')}"
        rul_text += f"\nDegradation: {rul_info.get('degradation_percent', 0)}%"
        rul_text += f"\nUrgency: {rul_info.get('urgency', 'MEDIUM')}"
    else:
        rul_text = ""
    
    # Step 3: Generate recommendations with LLM
    llm = get_llm_client()
    
    prompt = RECOMMENDATION_AGENT_PROMPT.format(
        equipment_type=equipment_type,
        equipment_id=equipment_id,
        diagnosis=diagnosis,
        root_causes=format_root_causes(root_causes),
        risk_level=risk_level,
        user_role=user_role,
        spare_parts=spare_parts_text,
        rul_prediction=rul_text,
        rag_context=rag_result.context if rag_result.grounded else "No procedures found.",
    )
    
    try:
        recommendation_output = llm.generate(prompt, max_tokens=1200, temperature=0.3)
        
        # Step 4: Parse recommendations
        recommendations = _parse_recommendations(recommendation_output)
        state["recommendations"] = recommendations
        
        # Extract cost and downtime estimates
        cost_match = re.search(r"ESTIMATED COST:\s*\$?([\d,]+)", recommendation_output)
        downtime_match = re.search(r"ESTIMATED DOWNTIME:\s*([\d.]+)\s*hours?", recommendation_output, re.IGNORECASE)
        
        if cost_match:
            state["metadata"]["estimated_cost"] = float(cost_match.group(1).replace(",", ""))
        if downtime_match:
            state["metadata"]["estimated_downtime_hours"] = float(downtime_match.group(1))
        
        # Store full recommendation text
        state["metadata"]["recommendation_details"] = recommendation_output
        
        # Update citations
        state["citations"].extend(_extract_citations_from_recommendations(recommendation_output, rag_result.sources))
        state["retrieved_chunks"].extend(rag_result.chunks)
        
        logger.info(f"✅ Recommendations complete: {len(recommendations)} actions prioritized")
        
    except Exception as e:
        logger.warning(f"Recommendation LLM unavailable (using rule-based recommendations): {e}")
        
        # Fallback: create rule-based recommendations
        recommendations = []
        
        # Priority 1: Immediate safety actions for CRITICAL/HIGH
        if risk_level in ["CRITICAL", "HIGH"]:
            recommendations.append(Recommendation(
                priority=1,
                action=f"Immediately inspect {equipment_type} {equipment_id} - {risk_level} condition detected",
                reason="Safety critical - requires urgent attention",
                estimated_time="1 hour",
                required_parts=[],
                safety_notes=["Follow LOTO procedures", "Notify supervisor", "Wear appropriate PPE"],
            ))
        
        # Priority 2: Address root causes
        for i, rc in enumerate(root_causes[:2], start=2):  # Top 2 root causes
            action_text = _create_action_from_cause(rc.cause, equipment_type)
            recommendations.append(Recommendation(
                priority=i,
                action=action_text,
                reason=rc.cause,
                estimated_time="2-4 hours",
                required_parts=_identify_parts([rc], rc.cause),
                safety_notes=["Follow LOTO procedures"],
            ))
        
        # Priority 3: Spare parts procurement
        if spare_parts_info:
            parts_list = [f"{p['part_number']} ({p['description']})" for p in spare_parts_info[:3]]
            recommendations.append(Recommendation(
                priority=len(recommendations) + 1,
                action=f"Procure required spare parts: {', '.join(parts_list)}",
                reason="Parts availability for repair",
                estimated_time="",
                required_parts=[p['part_number'] for p in spare_parts_info[:3]],
                safety_notes=[],
            ))
        
        # Priority 4: Post-repair monitoring
        recommendations.append(Recommendation(
            priority=len(recommendations) + 1,
            action=f"Monitor sensor readings for 24 hours after repair",
            reason="Verify repair effectiveness",
            estimated_time="24 hours",
            required_parts=[],
            safety_notes=[],
        ))
        
        state["recommendations"] = recommendations
        state["retrieved_chunks"].extend(rag_result.chunks)
        
        logger.info(f"✅ Rule-based recommendations complete: {len(recommendations)} actions prioritized")
    
    return state


def _identify_parts(root_causes: list, diagnosis: str) -> list[str]:
    """Identify likely spare parts from diagnosis text."""
    text = diagnosis + " " + " ".join(rc.cause for rc in root_causes)
    text_lower = text.lower()
    
    parts = []
    
    # Keyword mapping
    if "bearing" in text_lower:
        parts.append("bearing")
    if "seal" in text_lower:
        parts.append("motor_seal")
    if "lubrication" in text_lower or "lubricant" in text_lower:
        parts.append("lubricant")
    if "belt" in text_lower:
        parts.append("belt")
    if "pressure" in text_lower and "sensor" in text_lower:
        parts.append("pressure_sensor")
    
    return parts


def _parse_recommendations(text: str) -> list[Recommendation]:
    """Parse recommendation output into structured Recommendation objects."""
    recommendations = []
    
    # Find priority sections
    priority_sections = re.findall(
        r"PRIORITY\s+(\d+)[:\s-]+([A-Z\s]+):\s*(.+?)(?=PRIORITY\s+\d+|REQUIRED PARTS|POST-REPAIR|ESTIMATED|$)",
        text,
        re.DOTALL | re.IGNORECASE
    )
    
    for priority_num, section_name, section_content in priority_sections:
        # Parse steps
        steps = re.findall(r"Step\s+\d+:\s*(.+?)(?=Step\s+\d+:|$)", section_content, re.DOTALL)
        
        for step_text in steps:
            step_text = step_text.strip()
            if len(step_text) > 10:  # Skip empty/tiny steps
                # Extract any part references
                parts = re.findall(r"P/N:?\s*([\w-]+)", step_text)
                
                # Extract safety notes
                safety_notes = []
                if "lockout" in step_text.lower() or "loto" in step_text.lower():
                    safety_notes.append("LOTO required")
                if "ppe" in step_text.lower():
                    safety_notes.append("Wear appropriate PPE")
                
                recommendations.append(Recommendation(
                    priority=int(priority_num),
                    action=step_text[:200],  # Truncate if too long
                    reason=section_name.strip(),
                    estimated_time="",  # Will be in section header
                    required_parts=parts,
                    safety_notes=safety_notes,
                ))
    
    # If parsing failed, create at least one fallback
    if not recommendations:
        recommendations.append(Recommendation(
            priority=1,
            action="Follow standard maintenance procedure",
            reason="Automatic fallback",
            estimated_time="",
            required_parts=[],
            safety_notes=[],
        ))
    
    return recommendations[:10]  # Limit to top 10


def _extract_citations_from_recommendations(text: str, sources: list[dict]) -> list[dict]:
    """Extract citation markers from recommendations."""
    citations = []
    citation_markers = re.findall(r"\[(\d+)\]", text)
    
    for marker in set(citation_markers):
        idx = int(marker) - 1
        if 0 <= idx < len(sources):
            source = sources[idx]
            citations.append({
                "index": int(marker),
                "doc_name": source.get("doc_name", ""),
                "section": source.get("section", ""),
                "pages": source.get("pages", []),
            })
    
    return citations


def _create_action_from_cause(cause: str, equipment_type: str) -> str:
    """Create actionable recommendation from root cause."""
    cause_lower = cause.lower()
    
    if "bearing" in cause_lower:
        return f"Inspect and replace worn bearings on {equipment_type}"
    elif "lubrication" in cause_lower or "lubricant" in cause_lower:
        return f"Check lubrication system and replenish lubricant on {equipment_type}"
    elif "coolant" in cause_lower or "cooling" in cause_lower:
        return f"Inspect cooling system for leaks and verify coolant levels on {equipment_type}"
    elif "misalignment" in cause_lower or "alignment" in cause_lower:
        return f"Perform alignment check and adjustment on {equipment_type}"
    elif "sensor" in cause_lower:
        return f"Calibrate or replace faulty sensor on {equipment_type}"
    elif "leak" in cause_lower:
        return f"Locate and repair system leak on {equipment_type}"
    elif "overload" in cause_lower:
        return f"Reduce operating load and check capacity limits on {equipment_type}"
    else:
        return f"Inspect {equipment_type} for: {cause}"
