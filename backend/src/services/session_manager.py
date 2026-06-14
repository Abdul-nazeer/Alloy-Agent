"""
Session Manager Service
Manages multi-turn conversation history (sliding window).
"""

import logging
from collections import defaultdict, deque
from typing import Dict, List, Deque

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manage conversation history for multi-turn interactions.
    
    Uses sliding window: keep last 6 messages (3 user + 3 assistant).
    """
    
    def __init__(self, max_history: int = 6):
        self.max_history = max_history
        self._sessions: Dict[str, Deque[Dict[str, str]]] = defaultdict(
            lambda: deque(maxlen=self.max_history)
        )
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add message to session history."""
        self._sessions[session_id].append({
            "role": role,
            "content": content
        })
    
    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get conversation history for session."""
        return list(self._sessions[session_id])
    
    def format_history_for_prompt(self, session_id: str, max_chars_per_message: int = 300) -> str:
        """
        Format conversation history as text for LLM prompt.
        
        Returns:
            Formatted history string or empty if no history.
        """
        history = self.get_history(session_id)
        
        if not history:
            return ""
        
        lines = ["=== PREVIOUS CONVERSATION ==="]
        
        for msg in history:
            role = "Engineer" if msg["role"] == "user" else "Assistant"
            content = msg["content"]
            
            # Truncate long messages for context efficiency
            if len(content) > max_chars_per_message:
                content = content[:max_chars_per_message] + "..."
            
            lines.append(f"{role}: {content}")
        
        lines.append("=== END PREVIOUS CONVERSATION ===\n")
        
        return "\n".join(lines)
    
    def clear_session(self, session_id: str):
        """Clear session history."""
        if session_id in self._sessions:
            del self._sessions[session_id]
    
    def get_active_sessions_count(self) -> int:
        """Get number of active sessions."""
        return len(self._sessions)


# Singleton
_manager: SessionManager = None

def get_session_manager() -> SessionManager:
    global _manager
    if _manager is None:
        _manager = SessionManager()
    return _manager
