"""
Conversational Agent — Handles greetings and general inquiries
"""
import logging
from backend.src.agents.state import AgentState
from backend.src.agents.prompts import CONVERSATIONAL_PROMPT
from backend.src.agents.llm_client import get_llm_client

logger = logging.getLogger(__name__)


def conversational_node(state: AgentState) -> AgentState:
    """
    Handle conversational queries (greetings, general questions).
    
    Does NOT trigger diagnostic workflow - just responds naturally.
    """
    logger.info("💬 Conversational Agent executing...")
    
    try:
        query = state["query"]
        history = state.get("messages", [])
        
        # Build prompt
        prompt = CONVERSATIONAL_PROMPT.format(
            query=query,
            history=str(history[-5:]) if history else "None"
        )
        
        # Generate response
        llm = get_llm_client()
        response = llm.generate(prompt, max_tokens=200, temperature=0.7)
        
        # Update state
        state["final_answer"] = response.strip()
        state["completed_agents"].append("conversational")
        state["messages"].append({
            "agent": "conversational",
            "content": response.strip()
        })
        
        logger.info("✅ Conversational response generated")
        
    except Exception as e:
        logger.error(f"Conversational agent failed: {e}")
        
        # Fallback response
        query_lower = state["query"].lower()
        if any(greeting in query_lower for greeting in ["hi", "hello", "hey", "greetings"]):
            fallback = (
                "👋 Hello! I'm Alloy Agent, your AI maintenance assistant. "
                "I monitor equipment in real-time, detect anomalies, diagnose faults, "
                "and recommend repairs. How can I help you today?"
            )
        elif "what can you do" in query_lower or "capabilities" in query_lower or "help" in query_lower:
            fallback = (
                "I can:\n"
                "• Monitor sensors for Air Compressors, Cooling Fans, Rolling Mills, Conveyor Motors\n"
                "• Detect anomalies and predict failures before they happen\n"
                "• Diagnose root causes using maintenance manuals\n"
                "• Provide step-by-step repair procedures\n"
                "• Auto-generate reports when critical issues arise\n\n"
                "Try clicking on a machine card to see live sensor data, or ask me to analyze an equipment!"
            )
        else:
            fallback = (
                "I'm here to help with equipment maintenance! "
                "Ask me to analyze a machine, check for anomalies, or explain what I can do."
            )
        
        state["final_answer"] = fallback
        state["completed_agents"].append("conversational")
        state["errors"].append(f"LLM failed, used fallback response: {str(e)}")
    
    return state
