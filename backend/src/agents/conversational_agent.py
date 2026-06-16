"""
Conversational Agent — Handles greetings and general inquiries
"""
import logging
from backend.src.agents.state import AgentState
from backend.src.agents.prompts import CONVERSATIONAL_PROMPT
from backend.src.agents.llm_client import get_llm_client

logger = logging.getLogger(__name__)

# Import RAG for knowledge base queries
try:
    from backend.src.rag.pipeline import get_rag_pipeline
    RAG_AVAILABLE = True
    logger.info("✅ RAG pipeline imported successfully")
except ImportError as e:
    logger.warning(f"RAG not available: {e}")
    RAG_AVAILABLE = False


def conversational_node(state: AgentState) -> AgentState:
    """
    Handle conversational queries (greetings, general questions, status checks).
    
    Does NOT trigger diagnostic workflow - just responds naturally.
    Includes guardrails to stay within industrial maintenance domain.
    """
    logger.info("💬 Conversational Agent executing...")
    
    try:
        query = state["query"]
        history = state.get("messages", [])
        query_lower = query.lower()
        
        # Check if this is a status check with equipment data
        is_status_check = any(kw in query_lower for kw in ["status", "check", "how is", "tell me about"])
        equipment_id = state.get("equipment_id")
        sensor_readings = state.get("sensor_readings", [])
        
        # Guardrail: Check if query is completely off-topic
        # Equipment-related keywords
        equipment_keywords = [
            'equipment', 'machine', 'compressor', 'motor', 'fan', 'mill', 'conveyor',
            'sensor', 'temperature', 'pressure', 'vibration', 'rpm', 'maintenance',
            'repair', 'diagnose', 'fault', 'failure', 'anomaly', 'alert', 'breakdown',
            'lubrication', 'bearing', 'valve', 'pump', 'turbine', 'hydraulic',
            'monitor', 'predict', 'preventive', 'corrective', 'inspection',
            'AC-', 'CF-', 'RM-', 'CM-',  # Equipment ID patterns
            'status', 'check', 'how is',  # Status check keywords
            'recommendation', 'action', 'repair', 'fix', 'diagnosis', 'analysis',  # Added for progress clicks
            'show', 'tell', 'give'  # Action verbs for requesting information
        ]
        
        # Greeting keywords (allowed)
        greeting_keywords = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon']
        
        # Capability keywords (allowed)
        capability_keywords = ['what can you', 'help', 'capabilities', 'what do you do', 'who are you']
        
        # Document-related keywords (asking about PDFs, manuals, uploaded files)
        document_keywords = ['pdf', 'document', 'manual', 'file', 'uploaded', 'this document', 'paper', 'specification', 'datasheet']
        
        # Check if it's a greeting or capability question
        is_greeting = any(g in query_lower for g in greeting_keywords)
        is_capability = any(c in query_lower for c in capability_keywords)
        is_equipment_related = any(k in query_lower for k in equipment_keywords)
        is_document_query = any(k in query_lower for k in document_keywords)
        
        # If query is very short (< 3 words) and not greeting/capability, it might be off-topic
        word_count = len(query.split())
        
        # Guardrail: Reject completely off-topic questions
        # Allow: greetings, capability questions, equipment questions, document questions
        if not (is_greeting or is_capability or is_equipment_related or is_document_query) and word_count > 2:
            # This is likely an off-topic question
            off_topic_response = (
                "I'm specialized in industrial equipment maintenance and can only help with topics like "
                "equipment diagnostics, sensor analysis, maintenance procedures, and operational issues. "
                "Could you ask me something about your industrial equipment or maintenance needs?"
            )
            state["final_answer"] = off_topic_response
            state["completed_agents"].append("conversational")
            state["messages"].append({
                "agent": "conversational",
                "content": off_topic_response
            })
            logger.info("✅ Guardrail triggered - off-topic query rejected")
            return state
        
        # Special handling for status checks with sensor data
        if is_status_check and equipment_id and sensor_readings:
            logger.info(f"📊 Status check for {equipment_id} with sensor data")
            
            # Format sensor readings nicely
            sensor_summary = []
            for reading in sensor_readings[:5]:  # Limit to 5 sensors
                sensor_summary.append(
                    f"- {reading.sensor_type}: {reading.value:.2f} {reading.unit}"
                )
            
            status_response = f"""Current status of {equipment_id}:

{chr(10).join(sensor_summary)}

The equipment is currently operating. For detailed anomaly analysis, ask me to "detect anomalies" or "check for issues"."""
            
            state["final_answer"] = status_response
            state["completed_agents"].append("conversational")
            state["messages"].append({
                "agent": "conversational",
                "content": status_response
            })
            logger.info("✅ Status summary provided")
            return state
        
        # Determine if RAG should be used
        # Always use RAG for document-related queries (pdf, document, manual, etc.)
        document_keywords = ['pdf', 'document', 'manual', 'file', 'uploaded', 'this document', 'paper']
        is_document_query = any(k in query_lower for k in document_keywords)
        
        # Fetch relevant knowledge from RAG if:
        # 1. Equipment-related query, OR
        # 2. Document-related query (user asking about PDFs/manuals)
        rag_context = ""
        should_use_rag = (is_equipment_related or is_document_query) and RAG_AVAILABLE
        
        if should_use_rag:
            try:
                logger.info(f"🔍 Searching knowledge base for: {query[:100]}")
                rag_pipeline = get_rag_pipeline()
                rag_results = rag_pipeline.query(query, top_k=3)
                
                if rag_results and rag_results.get("context"):
                    rag_context = rag_results["context"]
                    # Add citations to state
                    if rag_results.get("sources"):
                        state["citations"] = rag_results["sources"]
                    logger.info(f"✅ Found {len(rag_results.get('sources', []))} relevant documents")
                else:
                    logger.info("No relevant documents found in knowledge base")
            except Exception as e:
                logger.warning(f"RAG search failed: {e}")
                # Continue without RAG context
        
        # Build prompt for in-scope queries
        if rag_context:
            # Enhanced prompt with RAG context AND conversation history for follow-ups
            history_text = ""
            if history and len(history) > 0:
                # Format last 3 exchanges for context
                recent_history = history[-6:]  # Last 3 Q&A pairs
                history_lines = []
                for msg in recent_history:
                    agent = msg.get("agent", "assistant")
                    content = msg.get("content", "")
                    if agent == "conversational":
                        history_lines.append(f"Assistant: {content[:200]}")  # Truncate long responses
                if history_lines:
                    history_text = "\n\nPREVIOUS CONVERSATION:\n" + "\n".join(history_lines[-4:])  # Last 2 exchanges
            
            prompt = f"""You are Alloy Agent, an AI maintenance assistant.

USER QUERY: {query}

KNOWLEDGE BASE INFORMATION:
{rag_context}{history_text}

INSTRUCTIONS:
- Answer the question DIRECTLY using the knowledge base
- If this is a follow-up question (e.g., "tell me more", "what about X"), use conversation history for context
- Be CONCISE - 2-4 sentences maximum
- NO greetings or introductions (unless user said "Hi")
- Jump straight to the answer

Answer:"""
        else:
            # Standard prompt without RAG
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
