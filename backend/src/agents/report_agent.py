"""
Report Agent — Structured maintenance report generation
"""

import logging
from datetime import datetime
from backend.src.agents.state import AgentState
from backend.src.agents.prompts import (
    REPORT_AGENT_PROMPT,
    format_anomalies,
    format_root_causes,
)
from backend.src.agents.llm_client import get_llm_client
from backend.src.agents.tools import logbook_append

logger = logging.getLogger(__name__)


def report_node(state: AgentState) -> AgentState:
    """
    Report Agent Node.
    
    Process:
    1. Aggregate findings from all agents
    2. Generate structured Markdown report
    3. Log to operations logbook
    4. Set final_answer
    
    Updates state:
    - report_content
    - final_answer
    """
    logger.info("📄 Report Agent executing...")
    
    state["completed_agents"].append("report")
    
    equipment_type = state.get("equipment_type", "Industrial Equipment")
    equipment_id = state.get("equipment_id", "Unknown")
    risk_level = state.get("risk_level", "UNKNOWN")
    
    # Determine report type based on risk level
    if state.get("requires_escalation"):
        report_type = "CRITICAL ALERT REPORT"
    else:
        report_type = "MAINTENANCE DECISION REPORT"
    
    # Step 1: Aggregate findings
    findings_summary = {
        "anomalies": format_anomalies(state.get("anomalies_detected", [])),
        "diagnosis": state.get("diagnosis", "No diagnosis performed"),
        "root_causes": format_root_causes(state.get("root_causes", [])),
        "risk_level": risk_level,
        "recommendations": _format_recommendations(state.get("recommendations", [])),
    }
    
    # Step 2: Generate report with LLM
    llm = get_llm_client()
    
    prompt = REPORT_AGENT_PROMPT.format(
        report_type=report_type,
        equipment_type=equipment_type,
        equipment_id=equipment_id,
        timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        **findings_summary
    )
    
    try:
        report_content = llm.generate(prompt, max_tokens=1000, temperature=0.1)
        
        # Clean up the report
        report_content = report_content.strip()
        
        # Add footer with citations
        if state.get("citations"):
            citations_section = "\n\n## Citations\n\n"
            for citation in state["citations"]:
                citations_section += f"[{citation['index']}] {citation['doc_name']}"
                if citation.get("section"):
                    citations_section += f" - {citation['section']}"
                if citation.get("pages"):
                    citations_section += f" (Pages: {', '.join(map(str, citation['pages']))})"
                citations_section += "\n"
            
            report_content += citations_section
        
        state["report_content"] = report_content
        
        # Step 3: Create final answer (shorter summary for chat)
        final_answer = _create_final_answer(state)
        state["final_answer"] = final_answer
        
        # Step 4: Log to operations logbook
        if equipment_id and equipment_id != "Unknown":
            logbook_append(
                equipment_id=equipment_id,
                entry_type="diagnosis" if state.get("diagnosis") else "inspection",
                summary=f"{risk_level} issue detected",
                details={
                    "query": state["query"],
                    "diagnosis": state.get("diagnosis"),
                    "risk_level": risk_level,
                    "actions_recommended": len(state.get("recommendations", [])),
                },
                engineer="AI Agent"
            )
        
        logger.info("✅ Report generation complete")
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=True)
        state["errors"].append(f"Report failed: {str(e)}")
        
        # Fallback: create basic report
        state["final_answer"] = _create_fallback_answer(state)
        state["report_content"] = state["final_answer"]
    
    return state


def _format_recommendations(recommendations: list) -> str:
    """Format recommendations for report."""
    if not recommendations:
        return "No specific recommendations generated"
    
    lines = []
    for rec in recommendations:
        lines.append(f"**Priority {rec.priority}** - {rec.action}")
        if rec.required_parts:
            lines.append(f"  - Parts: {', '.join(rec.required_parts)}")
        if rec.estimated_time:
            lines.append(f"  - Est. time: {rec.estimated_time}")
    
    return "\n".join(lines)


def _create_final_answer(state: AgentState) -> str:
    """Create concise final answer for chat interface."""
    parts = []
    
    # Summary line
    risk = state.get("risk_level", "UNKNOWN")
    equipment_id = state.get("equipment_id", "the equipment")
    
    if risk in ["CRITICAL", "HIGH"]:
        parts.append(f"🚨 **{risk} ISSUE DETECTED** for {equipment_id}")
    else:
        parts.append(f"✓ Analysis complete for {equipment_id} (Risk: {risk})")
    
    # Diagnosis
    if state.get("diagnosis"):
        parts.append(f"\n**Diagnosis:** {state['diagnosis']}")
    
    # Top root cause
    if state.get("root_causes"):
        top_cause = state["root_causes"][0]
        parts.append(f"\n**Root Cause:** {top_cause.cause} ({top_cause.confidence*100:.0f}% confidence)")
    
    # Top recommendation
    if state.get("recommendations"):
        top_rec = state["recommendations"][0]
        parts.append(f"\n**Immediate Action:** {top_rec.action}")
    
    # RUL if available
    if state.get("rul_estimate"):
        rul = state["rul_estimate"]
        parts.append(f"\n**Remaining Life:** {rul.get('estimate', 'Unknown')}")
    
    # Citations count
    if state.get("citations"):
        parts.append(f"\n\n*Based on {len(state['citations'])} source documents*")
    
    return "\n".join(parts)


def _create_fallback_answer(state: AgentState) -> str:
    """Create fallback answer when report generation fails."""
    return f"""Analysis completed for {state.get('equipment_id', 'equipment')}.

Risk Level: {state.get('risk_level', 'UNKNOWN')}

{state.get('diagnosis', 'Unable to complete full diagnosis.')}

Please review sensor data and consult maintenance manual for detailed guidance.
"""
