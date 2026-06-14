"""
FastAPI Routes for RAG and Agent chat.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

router = APIRouter(prefix="/api/v1", tags=["Alloy Agent"])


class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    context_used: bool


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Query the Alloy Agent for Decision Support using the new multi-agent system.
    """
    from backend.src.agents import chat
    
    try:
        result = chat(
            user_input=req.question,
            session_id=req.session_id or "default"
        )
        
        return ChatResponse(
            answer=result["response"],
            sources=[],
            context_used=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def rag_health():
    """Check if RAG routes are operational"""
    return {"status": "healthy", "service": "RAG routes"}
