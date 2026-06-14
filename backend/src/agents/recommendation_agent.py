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
    
    # Step 2: Lookup spare parts availability
    spare_parts_info = []
    
    # Try to identify required parts from root causes
    part_keywords = _identify_parts(root_causes, diagnosis)
    for keyword in part_keywords:
        part_data = spare_parts_lookup(keyword)
        if part_data:
            spare_parts_info.append(part_data)
    
    # Format spare parts for prompt
    if spare_parts_info:
        spare_parts_text = "\n".join([
            f"- {p['part_number']}: {p['description']} | "
            f"Stock: {p['in_stock']} | Lead time: {p['lead_time_days']} days | ${p['cost']}"
            for p in spare_parts_info
        ])
    else:
        spare_parts_text = "No specific parts identified. Generic spares available."
    
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
        rag_context=rag_result.context if rag_result.grounded else "No procedures found.",
    )
    
    try:
        recommendation_output = llm.generate(prompt, max_tokens=800, temperature=0.3)
        
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
        logger.error(f"Recommendation LLM failed: {e}", exc_info=True)
        state["errors"].append(f"Recommendation failed: {str(e)}")
        
        # Fallback: create basic recommendation
        state["recommendations"] = [
            Recommendation(
                priority=1,
                action=f"Inspect {equipment_type} and verify sensor readings",
                reason="Standard diagnostic procedure",
                estimated_time="2 hours",
                required_parts=[],
                safety_notes=["Follow LOTO procedures", "Wear appropriate PPE"],
            )
        ]
    
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
