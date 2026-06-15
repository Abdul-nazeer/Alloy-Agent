"""
Feedback Routes - Engineer feedback on AI recommendations
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.src.services.feedback_handler import get_feedback_handler
from backend.src.services.logbook import get_logbook_service

router = APIRouter(prefix="/feedback", tags=["feedback"])
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# Models
# ══════════════════════════════════════════════════════════════════════════════

class FeedbackSubmission(BaseModel):
    entry_id: str
    verdict: str  # "correct", "partially_correct", "incorrect"
    actual_root_cause: Optional[str] = None
    action_taken: Optional[str] = None
    outcome: Optional[str] = None
    downtime_hours: Optional[float] = None
    engineer_notes: Optional[str] = None


# ══════════════════════════════════════════════════════════════════════════════
# Feedback Submission
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/submit")
async def submit_feedback(feedback: FeedbackSubmission):
    """
    Submit engineer feedback on AI recommendation.
    
    If verdict is "incorrect", the correction will be indexed into RAG
    with a 1.3x boost for future retrievals.
    """
    try:
        handler = get_feedback_handler()
        
        result = handler.process_feedback(
            entry_id=feedback.entry_id,
            verdict=feedback.verdict,
            actual_root_cause=feedback.actual_root_cause,
            action_taken=feedback.action_taken,
            outcome=feedback.outcome,
            downtime_hours=feedback.downtime_hours,
            engineer_notes=feedback.engineer_notes
        )
        
        logger.info(f"✅ Feedback submitted for {feedback.entry_id}: {feedback.verdict}")
        
        return {
            "status": "success",
            "message": f"Feedback submitted successfully",
            "feedback_id": result["feedback_id"],
            "correction_indexed": result["correction_indexed"]
        }
        
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(500, f"Feedback submission failed: {str(e)}")


@router.get("/stats")
async def get_feedback_stats():
    """Get feedback statistics for system improvement tracking"""
    try:
        logbook = get_logbook_service()
        stats = logbook.get_feedback_stats()
        
        return {
            "status": "success",
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get feedback stats: {e}")
        raise HTTPException(500, str(e))


@router.get("/entry/{entry_id}")
async def get_entry_feedback(entry_id: str):
    """Get all feedback for a specific logbook entry"""
    try:
        logbook = get_logbook_service()
        entry = logbook.get_entry(entry_id)
        
        if not entry:
            raise HTTPException(404, f"Entry {entry_id} not found")
        
        return {
            "status": "success",
            "entry_id": entry_id,
            "feedback_history": entry.get("feedback_history", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get entry feedback: {e}")
        raise HTTPException(500, str(e))
