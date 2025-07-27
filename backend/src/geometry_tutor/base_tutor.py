"""
Base GeometryTutor class with common functionality for all tutor implementations.
"""

import time
from typing import Dict, Any, Optional
from abc import ABC
from langchain_core.runnables import RunnableConfig

from .core import GraphState, create_initial_state
from .graph import create_geometry_tutor_graph
from .llm_utils import setup_environment


class BaseGeometryTutor(ABC):
    """
    Base class for all GeometryTutor implementations.
    Contains common initialization and core functionality.
    """

    def __init__(self, strict_environment: bool = False):
        """
        Initialize the base geometry tutor.
        
        Args:
            strict_environment: If True, raise error on env setup failure.
                              If False, warn and continue (for CLI usage).
        """
        # Setup environment and check API keys
        if not setup_environment():
            if strict_environment:
                raise RuntimeError(
                    "Environment setup incomplete. Please check your API key configuration."
                )
            else:
                print("⚠️  Warning: Environment setup incomplete. Some features may not work.")
        
        self.graph = create_geometry_tutor_graph()
        self.current_state: Optional[GraphState] = None
        self.thread_id: Optional[str] = None

    def _create_thread_id(self, prefix: str = "geometry_session") -> str:
        """Create a unique thread ID for this session."""
        return f"{prefix}_{int(time.time())}"

    def _create_config(self) -> RunnableConfig:
        """Create a RunnableConfig for the current thread."""
        if not self.thread_id:
            self.thread_id = self._create_thread_id()
        return RunnableConfig({"configurable": {"thread_id": self.thread_id}})

    def reset_session(self):
        """Reset the current session."""
        self.current_state = None
        self.thread_id = None

    def get_basic_status(self) -> Dict[str, Any]:
        """Get basic status information common to all implementations."""
        if not self.current_state:
            return {"success": False, "error": "No active session"}
        
        return {
            "success": True,
            "session_active": True,
            "thread_id": self.thread_id,
            "session_complete": self.current_state.get("session_complete", False),
            "current_question_index": self.current_state.get("current_question_index", 0),
            "total_questions": len(self.current_state.get("questions", [])),
        }