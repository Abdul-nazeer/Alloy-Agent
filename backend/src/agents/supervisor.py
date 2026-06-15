"""
Supervisor Agent — LangGraph-based multi-agent orchestrator

Routes requests to specialist agents based on query type and context.
Implements stateful graph with conditional routing and loop prevention.
"""

import logging
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from backend.src.agents.state import AgentState
from backend.src.agents.anomaly_agent import anomaly_detection_node
from backend.src.agents.diagnosis_agent import diagnosis_node
from backend.src.agents.recommendation_agent import recommendation_node
from backend.src.agents.report_agent import report_node
from backend.src.agents.prompts import SUPERVISOR_ROUTING_PROMPT, format_sensor_readings
from backend.src.agents.llm_client import get_llm_client

logger = logging.getLogger(__name__)

# Maximum iterations to prevent infinite loops
MAX_ITERATIONS = 3


# ══════════════════════════════════════════════════════════════════════════════
# Supervisor Node
# ══════════════════════════════════════════════════════════════════════════════

def supervisor_node(state: AgentState) -> AgentState:
    """
    Supervisor routing decision node.
    
    Analyzes query + context and decides which agent to invoke next.
    Uses LLM for intelligent routing.
    """
    logger.info("🎯 Supervisor routing...")
    
    # Increment iteration count
    state["iteration_count"] = state.get("iteration_count", 0) + 1
    
    # Check iteration limit
    if state["iteration_count"] > MAX_ITERATIONS:
        logger.warning(f"Max iterations ({MAX_ITERATIONS}) reached, forcing report")
        state["next_agent"] = "report"
        return state
    
    query = state["query"]
    sensor_data = format_sensor_readings(state.get("sensor_readings", []))
    history = state.get("messages", [])
    
    # Build routing prompt
    llm = get_llm_client()
    
    prompt = SUPERVISOR_ROUTING_PROMPT.format(
        query=query,
        sensor_data=sensor_data if sensor_data != "No sensor data provided" else "None",
        history=str(history[-3:]) if history else "None",  # Last 3 messages
    )
    
    try:
        # Get routing decision from LLM
        routing_output = llm.generate(prompt, max_tokens=50, temperature=0.0)
        
        # Parse routing decision (should be: anomaly | diagnosis | recommendation | report)
        routing_output = routing_output.strip().lower()
        
        # Extract first valid agent name
        if "anomaly" in routing_output:
            next_agent = "anomaly"
        elif "diagnosis" in routing_output:
            next_agent = "diagnosis_agent"
        elif "recommendation" in routing_output:
            next_agent = "recommendation"
        elif "report" in routing_output:
            next_agent = "report"
        else:
            # Fallback routing logic
            next_agent = _fallback_routing(state)
        
        # Skip already completed agents (except report which is always terminal)
        if next_agent in state.get("completed_agents", []) and next_agent != "report":
            logger.info(f"Agent '{next_agent}' already completed, routing to report")
            next_agent = "report"
        
        state["next_agent"] = next_agent
        logger.info(f"✓ Routing to: {next_agent}")
        
    except Exception as e:
        logger.error(f"Supervisor routing failed: {e}")
        state["errors"].append(f"Routing failed: {str(e)}")
        state["next_agent"] = _fallback_routing(state)
    
    return state


def _fallback_routing(state: AgentState) -> str:
    """
    Deterministic fallback routing when LLM routing fails.
    """
    completed = state.get("completed_agents", [])
    
    # If we have sensor readings and haven't checked anomalies → anomaly
    if state.get("sensor_readings") and "anomaly" not in completed:
        return "anomaly"
    
    # If we have anomalies or query asks "why" → diagnosis
    if (state.get("anomalies_detected") or 
        any(word in state["query"].lower() for word in ["why", "cause", "diagnose", "wrong"])):
        if "diagnosis_agent" not in completed:
            return "diagnosis_agent"
    
    # If we have diagnosis → recommendation
    if state.get("diagnosis") and "recommendation" not in completed:
        return "recommendation"
    
    # Default → report
    return "report"


# ══════════════════════════════════════════════════════════════════════════════
# Routing Decision Function
# ══════════════════════════════════════════════════════════════════════════════

def route_decision(state: AgentState) -> Literal["anomaly", "diagnosis_agent", "recommendation", "report", "end"]:
    """
    Conditional edge function that determines next node based on state.
    """
    next_agent = state.get("next_agent")
    
    # If report is complete, end
    if "report" in state.get("completed_agents", []):
        return "end"
    
    # Route to selected agent
    if next_agent == "anomaly":
        return "anomaly"
    elif next_agent == "diagnosis_agent":
        return "diagnosis_agent"
    elif next_agent == "recommendation":
        return "recommendation"
    elif next_agent == "report":
        return "report"
    else:
        # Fallback to report
        return "report"


# ══════════════════════════════════════════════════════════════════════════════
# Build LangGraph
# ══════════════════════════════════════════════════════════════════════════════

def build_agent_graph() -> StateGraph:
    """
    Build the multi-agent LangGraph.
    
    Graph structure:
    
    START → supervisor → [anomaly | diagnosis | recommendation] → supervisor → ... → report → END
    
    The supervisor can route back to itself for multi-step reasoning,
    but is limited by MAX_ITERATIONS to prevent infinite loops.
    """
    workflow = StateGraph(AgentState)
    
    # Add all nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("anomaly", anomaly_detection_node)
    workflow.add_node("diagnosis_agent", diagnosis_node)
    workflow.add_node("recommendation", recommendation_node)
    workflow.add_node("report", report_node)
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Conditional routing from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        route_decision,
        {
            "anomaly": "anomaly",
            "diagnosis_agent": "diagnosis_agent",
            "recommendation": "recommendation",
            "report": "report",
            "end": END,
        }
    )
    
    # All specialist agents loop back to supervisor for next decision
    # (Supervisor will route to report after all agents complete)
    workflow.add_edge("anomaly", "supervisor")
    workflow.add_edge("diagnosis_agent", "supervisor")
    workflow.add_edge("recommendation", "supervisor")
    
    # Report is terminal
    workflow.add_edge("report", END)
    
    return workflow


# ══════════════════════════════════════════════════════════════════════════════
# Compiled Graph with Memory
# ══════════════════════════════════════════════════════════════════════════════

# Build and compile the graph
_graph = build_agent_graph()
_memory = MemorySaver()  # In-memory checkpointer for multi-turn conversations

# Compile with memory checkpointing
agent_graph = _graph.compile(checkpointer=_memory)

logger.info("✅ Multi-agent graph compiled with memory checkpointing")


# ══════════════════════════════════════════════════════════════════════════════
# Public API
# ══════════════════════════════════════════════════════════════════════════════

def run_agent_graph(state: AgentState, session_id: str = "default") -> AgentState:
    """
    Execute the agent graph with a given state.
    
    Args:
        state: Initial agent state
        session_id: Session ID for multi-turn memory
    
    Returns:
        Final state after graph execution
    """
    try:
        # Run graph with checkpointing
        config = {"configurable": {"thread_id": session_id}}
        
        logger.info(f"Starting graph execution (session: {session_id})")
        
        # Execute graph
        final_state = agent_graph.invoke(state, config)
        
        logger.info(f"Graph execution complete. Agents executed: {final_state.get('completed_agents', [])}")
        
        return final_state
        
    except Exception as e:
        logger.error(f"Graph execution failed: {e}", exc_info=True)
        
        # Return state with error
        state["errors"].append(f"Graph execution failed: {str(e)}")
        state["final_answer"] = f"I encountered an error: {str(e)}"
        return state


def get_conversation_history(session_id: str) -> list:
    """
    Retrieve conversation history for a session.
    
    Args:
        session_id: Session identifier
    
    Returns:
        List of message dicts
    """
    try:
        # Get checkpoint from memory
        config = {"configurable": {"thread_id": session_id}}
        checkpoint = _memory.get(config)
        
        if checkpoint and "messages" in checkpoint:
            return checkpoint["messages"]
        
        return []
        
    except Exception as e:
        logger.error(f"Failed to retrieve history: {e}")
        return []
