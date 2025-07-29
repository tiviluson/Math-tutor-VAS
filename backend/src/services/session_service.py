"""
Session Service for managing tutoring sessions.
Handles session creation, storage, and lifecycle management.
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

from src.api.api_tutor import ApiGeometryTutor


class SessionRepository(ABC):
    """Abstract base class for session storage implementations."""
    
    @abstractmethod
    def create_session(self, session_id: str, tutor: ApiGeometryTutor) -> None:
        """Store a new session."""
        pass
    
    @abstractmethod
    def get_session(self, session_id: str) -> Optional[ApiGeometryTutor]:
        """Retrieve a session by ID."""
        pass
    
    @abstractmethod
    def delete_session(self, session_id: str) -> None:
        """Delete a session."""
        pass
    
    @abstractmethod
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count of cleaned sessions."""
        pass
    
    @abstractmethod
    def get_session_metadata(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session metadata without the tutor instance."""
        pass
    
    @abstractmethod
    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions."""
        pass


class InMemorySessionRepository(SessionRepository):
    """In-memory implementation of session repository."""
    
    def __init__(self, session_timeout: timedelta = timedelta(hours=2)):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = session_timeout
    
    def create_session(self, session_id: str, tutor: ApiGeometryTutor) -> None:
        """Store a new session."""
        self.sessions[session_id] = {
            "tutor": tutor,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "active": True,
        }
    
    def get_session(self, session_id: str) -> Optional[ApiGeometryTutor]:
        """Retrieve a session by ID, return None if not found or expired."""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session is expired
        if datetime.now() - session["last_activity"] > self.session_timeout:
            self.delete_session(session_id)
            return None
        
        # Update last activity
        session["last_activity"] = datetime.now()
        return session["tutor"]
    
    def delete_session(self, session_id: str) -> None:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count of cleaned sessions."""
        expired_sessions = []
        current_time = datetime.now()
        
        for session_id, session in self.sessions.items():
            if current_time - session["last_activity"] > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.delete_session(session_id)
        
        return len(expired_sessions)
    
    def get_session_metadata(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session metadata without the tutor instance."""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        return {
            "session_id": session_id,
            "created_at": session["created_at"],
            "last_activity": session["last_activity"],
            "active": session["active"],
        }
    
    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions."""
        active_sessions = []
        
        for session_id, session_data in self.sessions.items():
            active_sessions.append({
                "session_id": session_id,
                "created_at": session_data["created_at"].isoformat(),
                "last_activity": session_data["last_activity"].isoformat(),
                "active": session_data["active"],
            })
        
        return active_sessions


class SessionService:
    """
    Service for managing tutoring sessions.
    Provides high-level session management operations.
    """
    
    def __init__(self, repository: Optional[SessionRepository] = None):
        """
        Initialize the session service.
        
        Args:
            repository: Session repository implementation. Defaults to InMemorySessionRepository.
        """
        self.repository = repository or InMemorySessionRepository()
    
    def create_session(self, problem_text: str) -> Dict[str, Any]:
        """
        Create a new tutoring session.
        
        Args:
            problem_text: The geometry problem text
            
        Returns:
            Dictionary with session creation result
        """
        try:
            # Create tutor instance
            tutor = ApiGeometryTutor()
            
            # Generate unique session ID
            session_id = str(uuid.uuid4())
            
            # Store session
            self.repository.create_session(session_id, tutor)
            
            # Start the problem
            result = tutor.start_problem(problem_text)
            
            if not result["success"]:
                self.repository.delete_session(session_id)
                return {
                    "success": False,
                    "error": result["error"]
                }
            
            return {
                "success": True,
                "session_id": session_id,
                "message": "Session created successfully",
                "total_questions": result.get("total_questions", 0),
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create session: {str(e)}"
            }
    
    def get_session(self, session_id: str) -> Optional[ApiGeometryTutor]:
        """Get a session by ID."""
        return self.repository.get_session(session_id)
    
    def delete_session(self, session_id: str) -> Dict[str, Any]:
        """
        Delete a session.
        
        Args:
            session_id: The session ID to delete
            
        Returns:
            Dictionary with deletion result
        """
        metadata = self.repository.get_session_metadata(session_id)
        if not metadata:
            return {
                "success": False,
                "error": "Session not found"
            }
        
        self.repository.delete_session(session_id)
        return {
            "success": True,
            "message": "Session deleted successfully"
        }
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session metadata."""
        return self.repository.get_session_metadata(session_id)
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count."""
        return self.repository.cleanup_expired_sessions()
    
    def list_active_sessions(self) -> Dict[str, Any]:
        """List all active sessions."""
        sessions = self.repository.list_active_sessions()
        return {
            "active_sessions": len(sessions),
            "sessions": sessions
        }
    
    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists and is active."""
        return self.get_session(session_id) is not None