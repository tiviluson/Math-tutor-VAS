"""
Interactive GeometryTutor for CLI usage.
Provides interactive console-based tutoring session.
"""

from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from .base_tutor import BaseGeometryTutor
from .core import create_initial_state


class InteractiveGeometryTutor(BaseGeometryTutor):
    """
    Interactive GeometryTutor class for CLI usage.
    Provides console-based interactive tutoring sessions.
    """

    def __init__(self):
        # Use non-strict environment (warn but continue)
        super().__init__(strict_environment=False)

    def start_new_problem(self, problem_text: str) -> Dict[str, Any]:
        """
        Start a new geometry problem session with integrated interactive mode.
        This method automatically runs the interactive session within the graph flow.

        Args:
            problem_text: The Vietnamese geometry problem text

        Returns:
            Dictionary with session completion status
        """
        # Create initial state
        initial_state = create_initial_state(problem_text)

        # Generate a unique thread ID for this session
        self.thread_id = self._create_thread_id()

        # Run the complete interactive session within the graph
        config = self._create_config()

        try:
            print("🚀 Bắt đầu phiên học AI Geometry Tutor")
            print("=" * 60)
            
            # Execute the graph workflow (this will run interactively)
            final_state = self.graph.invoke(initial_state, config=config)
            self.current_state = final_state

            # Check final status
            if final_state.get("session_complete"):
                print("\n🎉 Phiên học hoàn tất!")
                return {
                    "success": True,
                    "session_complete": True,
                    "message": "Interactive session completed successfully"
                }
            else:
                print("\n👋 Phiên học kết thúc.")
                return {
                    "success": True,
                    "session_complete": False,
                    "message": "Interactive session ended by user"
                }

        except KeyboardInterrupt:
            print("\n👋 Phiên học bị gián đoạn bởi người dùng")
            return {
                "success": False,
                "session_complete": False,
                "error": "Session interrupted by user"
            }
        except Exception as e:
            print(f"\n❌ Lỗi trong phiên học: {str(e)}")
            return {
                "success": False,
                "session_complete": False,
                "error": f"Session error: {str(e)}"
            }

    def get_current_status(self) -> Dict[str, Any]:
        """Get the current status of the tutoring session (interactive version)."""
        basic_status = self.get_basic_status()
        
        if not basic_status["success"]:
            return basic_status

        # Add interactive-specific status information
        status = basic_status.copy()
        status.update({
            "mode": "interactive",
            "known_facts": self.current_state.get("known_facts", []),
            "hint_level": self.current_state.get("hint_level", 0),
            "is_validated": self.current_state.get("is_validated", False),
        })

        # Add current question if available
        current_index = self.current_state.get("current_question_index", 0)
        questions = self.current_state.get("questions", [])
        if current_index < len(questions):
            status["current_question"] = questions[current_index]
        
        return status

    def visualize_graph(self):
        """Visualize the LangGraph workflow structure (development utility)."""
        try:
            # This would require additional dependencies for graph visualization
            print("📊 Graph Visualization:")
            print("Available in future versions with graphviz support")
            # For now, just show the node structure
            print("Nodes: parse_problem → reason_and_solve → await_user_action")
            print("       ↓ generate_hint ↓ validate_solution ↓ generate_solution")
            print("       → move_to_next_question → END")
        except Exception as e:
            print(f"❌ Error visualizing graph: {e}")


def create_tutor() -> InteractiveGeometryTutor:
    """Factory function to create a new interactive geometry tutor instance."""
    return InteractiveGeometryTutor()