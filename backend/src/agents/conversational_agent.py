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
    This is for CHAT ONLY - uses RAG for knowledge-based answers.
    Sensor data analysis should ONLY happen through anomaly/diagnosis agents.
    """
    logger.info("💬 Conversational Agent executing...")
    
    try:
        query = state["query"]
        history = state.get("messages", [])
        query_lower = query.lower()
        
        # Guardrail: STRICT - Chat is for knowledge only, NOT for sensor analysis
        # Block any queries that look like they want anomaly detection or diagnosis
        diagnosis_keywords = ['sensor', 'reading', 'current', 'now', 'detect', 'anomaly', 'diagnose', 'analyze', 'check status']
        is_diagnosis_query = any(kw in query_lower for kw in diagnosis_keywords)
        
        if is_diagnosis_query:
            diagnosis_redirect = (
                "I can provide general maintenance knowledge, but for real-time sensor analysis and diagnostics, "
                "please click on an equipment card or use the 'Detect Anomaly' button. "
                "That will trigger the full diagnostic workflow with sensor data analysis."
            )
            state["final_answer"] = diagnosis_redirect
            state["completed_agents"].append("conversational")
            state["messages"].append({
                "agent": "conversational",
                "content": diagnosis_redirect
            })
            logger.info("✅ Diagnosis query blocked - redirecting to anomaly detection")
            return state
        
        # Equipment-related keywords for RAG queries (general knowledge ONLY)
        equipment_keywords = [
            'equipment', 'machine', 'compressor', 'motor', 'fan', 'mill', 'conveyor',
            'maintenance', 'repair', 'procedure', 'manual', 'how to', 'what is',
            'lubrication', 'bearing', 'valve', 'pump', 'turbine', 'hydraulic',
            'preventive', 'corrective', 'inspection', 'how', 'what', 'why', 'when'
        ]
        
        # Greeting keywords (allowed)
        greeting_keywords = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon']
        
        # Capability keywords (allowed)
        capability_keywords = ['what can you', 'help', 'capabilities', 'what do you do', 'who are you']
        
        # Document-related keywords (asking about PDFs, manuals, uploaded files)
        document_keywords = ['pdf', 'document', 'manual', 'file', 'uploaded', 'this document', 'paper', 'specification', 'datasheet', 'in the', 'about the']
        
        # Check if it's a greeting or capability question
        is_greeting = any(g in query_lower for g in greeting_keywords)
        is_capability = any(c in query_lower for c in capability_keywords)
        is_equipment_related = any(k in query_lower for k in equipment_keywords)
        is_document_query = any(k in query_lower for k in document_keywords)
        
        # If query is very short (< 3 words) and not greeting/capability, it might be off-topic
        word_count = len(query.split())
        
        # Guardrail: Reject completely off-topic questions
        if not (is_greeting or is_capability or is_equipment_related or is_document_query):
            if word_count > 2 and word_count < 20:
                technical_terms = ['system', 'data', 'information', 'details', 'explain', 'describe', 'show', 'tell']
                has_technical_term = any(term in query_lower for term in technical_terms)
                
                if not has_technical_term:
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
        
        # Fetch relevant knowledge from RAG if equipment/document related
        rag_context = ""
        should_use_rag = (is_equipment_related or is_document_query) and RAG_AVAILABLE
        
        if should_use_rag:
            try:
                logger.info(f"🔍 Searching knowledge base for: {query[:100]}")
                rag_pipeline = get_rag_pipeline()
                rag_results = rag_pipeline.query(query, top_k=3)
                
                if rag_results and rag_results.get("context"):
                    rag_context = rag_results["context"]
                    if rag_results.get("sources"):
                        state["citations"] = rag_results["sources"]
                    logger.info(f"✅ Found {len(rag_results.get('sources', []))} relevant documents")
                else:
                    logger.info("No relevant documents found in knowledge base")
            except Exception as e:
                logger.warning(f"RAG search failed: {e}")
        
        # Build prompt for in-scope queries
        if rag_context:
            # Enhanced prompt with RAG context AND conversation history for follow-ups
            history_text = ""
            if history and len(history) > 0:
                recent_history = history[-6:]
                history_lines = []
                for msg in recent_history:
                    agent = msg.get("agent", "assistant")
                    content = msg.get("content", "")
                    if agent == "conversational":
                        history_lines.append(f"Assistant: {content[:200]}")
                if history_lines:
                    history_text = "\n\nPREVIOUS CONVERSATION:\n" + "\n".join(history_lines[-4:])
            
            prompt = f"""You are Alloy Agent, an AI maintenance assistant specializing in industrial equipment.

USER QUERY: {query}

KNOWLEDGE BASE INFORMATION:
{rag_context}{history_text}

INSTRUCTIONS:
- Answer using ONLY the knowledge base information provided
- Be specific and technical - cite procedures, specifications, maintenance intervals
- If this is a follow-up question, use conversation history for context
- Keep answers focused: 3-5 sentences for general questions, more detail for procedures
- DO NOT analyze sensor data or diagnose current faults (that's for diagnosis mode)
- Focus on maintenance knowledge, procedures, and best practices
- If asked about current equipment status, tell user to click equipment card or use "Detect Anomaly" button

Answer:"""
        else:
            # Standard conversational prompt without RAG
            prompt = CONVERSATIONAL_PROMPT.format(
                query=query,
                history=str(history[-5:]) if history else "None"
            )
        
        # Generate response
        llm = get_llm_client()
        response = llm.generate(prompt, max_tokens=800, temperature=0.7)
        
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
