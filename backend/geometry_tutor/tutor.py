"""
Main GeometryTutor class providing a clean interface for the AI Geometry Tutor system.
"""

import time
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from .core import GraphState, create_initial_state
from .graph import create_geometry_tutor_graph
from .llm_utils import setup_environment


class GeometryTutor:
    """
    Main class for the AI Geometry Tutor system.
    Provides a clean interface for interacting with the LangGraph workflow.
    """

    def __init__(self):
        # Setup environment and check API keys
        if not setup_environment():
            print("⚠️  Warning: Environment setup incomplete. Some features may not work.")
        
        self.graph = create_geometry_tutor_graph()
        self.current_state = None  # type: ignore
        self.thread_id = None

    def start_new_problem(self, problem_text: str) -> Dict[str, Any]:
        """
        Start a new geometry problem session with integrated interactive mode.
        This method now automatically runs the interactive session within the graph flow.

        Args:
            problem_text: The Vietnamese geometry problem text

        Returns:
            Dictionary with session completion status
        """
        # Create initial state
        initial_state = create_initial_state(problem_text)

        # Generate a unique thread ID for this session
        self.thread_id = f"geometry_session_{int(time.time())}"

        # Run the complete interactive session within the graph
        config = RunnableConfig({"configurable": {"thread_id": self.thread_id}})

        try:
            print("🚀 Bắt đầu phiên học AI Geometry Tutor")
            print("=" * 60)

            # Set initial action to start the session
            initial_state["user_action"] = "start"

            # Execute the graph with the new interactive flow
            for state in self.graph.stream(initial_state, config):
                self.current_state: dict = list(state.values())[0]

                # Break if session is complete or error occurred
                if self.current_state.get("session_complete") or self.current_state.get(
                    "error_message"
                ):
                    break

            if self.current_state.get("error_message"):
                return {"success": False, "error": self.current_state["error_message"]}

            return {
                "success": True,
                "session_complete": self.current_state.get("session_complete", False),
                "total_questions": len(self.current_state.get("questions", [])),
                "message": "Phiên học đã hoàn thành thành công!",
            }

        except Exception as e:
            return {"success": False, "error": f"Lỗi trong phiên học: {str(e)}"}

    def get_current_status(self) -> Dict[str, Any]:
        """Get the current status of the tutoring session."""
        if not self.current_state:
            return {"success": False, "error": "Chưa có bài toán nào được khởi tạo"}

        return {
            "success": True,
            "current_question_index": self.current_state["current_question_index"] + 1,
            "total_questions": len(self.current_state["questions"]),
            "current_question": (
                self.current_state["questions"][
                    self.current_state["current_question_index"]
                ]
                if self.current_state["current_question_index"]
                < len(self.current_state["questions"])
                else ""
            ),
            "hint_level": self.current_state["hint_level"],
            "hints_used": len(self.current_state["generated_hints"]),
            "is_validated": self.current_state["is_validated"],
            "session_complete": self.current_state["session_complete"],
            "known_facts": self.current_state["known_facts"],
        }

    def visualize_graph(self):
        """Display the graph structure if in a Jupyter environment."""
        try:
            from IPython.display import Image, display
            display(Image(self.graph.get_graph().draw_mermaid_png()))
        except ImportError:
            print("Graph visualization requires IPython/Jupyter environment")
        except Exception as e:
            print(f"Error visualizing graph: {e}")


def create_tutor() -> GeometryTutor:
    """Convenience function to create a new GeometryTutor instance."""
    return GeometryTutor()
