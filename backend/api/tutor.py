"""
Enhanced GeometryTutor for API usage.
This version provides non-interactive methods for API integration.
"""

import time
from typing import Dict, Any, Optional, List
from langchain_core.runnables import RunnableConfig

from geometry_tutor.core import GraphState, create_initial_state
from geometry_tutor.graph import create_geometry_tutor_graph
from geometry_tutor.llm_utils import setup_environment
from geometry_tutor.agents import (
    parse_problem,
    reason_and_solve,
    generate_hint,
    validate_solution,
    generate_solution,
    move_to_next_question,
)


class ApiGeometryTutor:
    """
    Enhanced GeometryTutor class specifically designed for API usage.
    Provides non-interactive methods for programmatic access.
    """

    def __init__(self):
        # Setup environment and check API keys
        if not setup_environment():
            raise RuntimeError(
                "Environment setup incomplete. Please check your API key configuration."
            )

        self.graph = create_geometry_tutor_graph()
        self.current_state: Optional[GraphState] = None
        self.thread_id: Optional[str] = None

    def start_problem(self, problem_text: str) -> Dict[str, Any]:
        """
        Start a new geometry problem session (non-interactive).

        Args:
            problem_text: The Vietnamese geometry problem text

        Returns:
            Dictionary with session setup status
        """
        # Create initial state
        initial_state = create_initial_state(problem_text)

        # Generate a unique thread ID for this session
        self.thread_id = f"api_session_{int(time.time())}"

        try:
            # Parse the problem
            parsed_state = parse_problem(initial_state)

            if parsed_state.get("error_message"):
                return {"success": False, "error": parsed_state["error_message"]}

            # Reason and solve for the first question
            if parsed_state["questions"]:
                solved_state = reason_and_solve(parsed_state)
                self.current_state = solved_state
            else:
                self.current_state = parsed_state

            return {
                "success": True,
                "total_questions": len(self.current_state["questions"]),
                "current_question_index": self.current_state["current_question_index"],
                "current_question": (
                    self.current_state["questions"][0]
                    if self.current_state["questions"]
                    else ""
                ),
                "message": "Problem parsed and ready for interaction",
            }

        except Exception as e:
            return {"success": False, "error": f"Error starting problem: {str(e)}"}

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the tutoring session."""
        if not self.current_state:
            return {"success": False, "error": "No active session"}

        try:
            current_question = ""
            if self.current_state["current_question_index"] < len(
                self.current_state["questions"]
            ):
                current_question = self.current_state["questions"][
                    self.current_state["current_question_index"]
                ]

            return {
                "success": True,
                "current_question_index": self.current_state["current_question_index"]
                + 1,
                "total_questions": len(self.current_state["questions"]),
                "current_question": current_question,
                "hint_level": self.current_state["hint_level"],
                "hints_used": len(self.current_state["generated_hints"]),
                "is_validated": self.current_state["is_validated"],
                "session_complete": self.current_state["session_complete"],
                "known_facts": self.current_state["known_facts"],
                "illustration_steps": self.current_state.get("illustration_steps", []),
            }

        except Exception as e:
            return {"success": False, "error": f"Error getting status: {str(e)}"}

    def request_hint(self) -> Dict[str, Any]:
        """Request a hint for the current question."""
        if not self.current_state:
            return {"success": False, "error": "No active session"}

        try:
            if self.current_state["hint_level"] >= 3:
                return {
                    "success": False,
                    "error": "Đã đạt số gợi ý tối đa cho câu hỏi này",
                    "hint_level": self.current_state["hint_level"],
                    "max_hints_reached": True,
                }

            # Generate hint using the agent
            hint_state = generate_hint(self.current_state)
            self.current_state = hint_state

            if hint_state.get("error_message"):
                return {"success": False, "error": hint_state["error_message"]}

            latest_hint = (
                hint_state["generated_hints"][-1]
                if hint_state["generated_hints"]
                else "No hint available"
            )

            return {
                "success": True,
                "hint_text": latest_hint,
                "hint_level": hint_state["hint_level"],
                "max_hints_reached": hint_state["hint_level"] >= 3,
            }

        except Exception as e:
            return {"success": False, "error": f"Error generating hint: {str(e)}"}

    def validate_user_solution(self, user_input: str) -> Dict[str, Any]:
        """Validate a user's solution for the current question."""
        if not self.current_state:
            return {"success": False, "error": "No active session"}

        if not user_input or not user_input.strip():
            return {"success": False, "error": "Solution text cannot be empty"}

        try:
            # Set user solution in state
            self.current_state["user_solution_attempt"] = user_input

            # Validate using the agent
            validated_state = validate_solution(self.current_state)
            self.current_state = validated_state

            if validated_state.get("error_message"):
                return {"success": False, "error": validated_state["error_message"]}

            # Parse the final answer to extract feedback and score
            final_answer = validated_state.get("final_answer", "")
            is_correct = validated_state.get("is_validated", False)
            input_type = validated_state.get("user_input_type", "unknown")

            # Get the actual validation score from the state
            # For questions, use a default score since they don't get validated
            if input_type == "question":
                score = 0  # Questions don't have a score
            else:
                score = validated_state.get(
                    "validation_score", 85 if is_correct else 45
                )

            # Simple parsing of the feedback (in real implementation, this would be more structured)
            feedback = final_answer

            # Determine message type based on input type and validation result
            if input_type == "question":
                message_type = "answer"
            elif is_correct:
                message_type = "validation_success"
            else:
                message_type = "validation_feedback"

            return {
                "success": True,
                "is_correct": is_correct,
                "feedback": feedback,
                "score": score,
                "input_type": input_type,
                "message_type": message_type,
            }

        except Exception as e:
            return {"success": False, "error": f"Error validating solution: {str(e)}"}

    def get_complete_solution(self) -> Dict[str, Any]:
        """Get the complete solution for the current question."""
        if not self.current_state:
            return {"success": False, "error": "No active session"}

        try:
            # Generate solution using the agent
            solution_state = generate_solution(self.current_state)
            self.current_state = solution_state

            if solution_state.get("error_message"):
                return {"success": False, "error": solution_state["error_message"]}

            return {
                "success": True,
                "solution_text": solution_state.get(
                    "final_answer", "Solution not available"
                ),
            }

        except Exception as e:
            return {"success": False, "error": f"Error generating solution: {str(e)}"}

    def move_to_next_question(self) -> Dict[str, Any]:
        """Move to the next question in the problem."""
        if not self.current_state:
            return {"success": False, "error": "No active session"}

        try:
            # Check if current question is validated
            # if not self.current_state.get("is_validated", False):
            #     return {
            #         "success": False,
            #         "error": "Current question must be validated before moving to next",
            #     }

            # Move to next question
            next_state = move_to_next_question(self.current_state)

            # If not complete, prepare the next question
            if not next_state["session_complete"]:
                # Reason and solve for the new question
                solved_state = reason_and_solve(next_state)
                self.current_state = solved_state
            else:
                self.current_state = next_state

            return {
                "success": True,
                "session_complete": self.current_state["session_complete"],
                "current_question_index": self.current_state["current_question_index"],
                "message": (
                    "Session complete!"
                    if self.current_state["session_complete"]
                    else "Moved to next question"
                ),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error moving to next question: {str(e)}",
            }

    def get_current_question(self) -> Dict[str, Any]:
        """Get the current question details."""
        if not self.current_state:
            return {"success": False, "error": "No active session"}

        try:
            if self.current_state["current_question_index"] >= len(
                self.current_state["questions"]
            ):
                return {"success": True, "question": "", "session_complete": True}

            current_question = self.current_state["questions"][
                self.current_state["current_question_index"]
            ]

            return {
                "success": True,
                "question": current_question,
                "question_index": self.current_state["current_question_index"] + 1,
                "total_questions": len(self.current_state["questions"]),
                "session_complete": False,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting current question: {str(e)}",
            }

    def reset_session(self):
        """Reset the current session."""
        self.current_state = None
        self.thread_id = None

    def get_enhanced_status(self) -> Dict[str, Any]:
        """Get enhanced status including original problem, solved questions, and current solution if validated."""
        if not self.current_state:
            return {"success": False, "error": "No active session"}

        try:
            current_question = ""
            if self.current_state["current_question_index"] < len(
                self.current_state["questions"]
            ):
                current_question = self.current_state["questions"][
                    self.current_state["current_question_index"]
                ]

            # Get previously solved questions (questions before current index)
            previously_solved = []
            for i in range(self.current_state["current_question_index"]):
                question_data = {
                    "question_index": i + 1,
                    "question_text": self.current_state["questions"][i],
                    "solved": True,
                }
                previously_solved.append(question_data)

            # Get current question solution if it's validated
            current_solution = None
            if self.current_state["is_validated"] and self.current_state.get(
                "final_answer"
            ):
                current_solution = self.current_state["final_answer"]

            return {
                "success": True,
                "current_question_index": self.current_state["current_question_index"],
                "total_questions": len(self.current_state["questions"]),
                "current_question": current_question,
                "hint_level": self.current_state["hint_level"],
                "hints_used": len(self.current_state["generated_hints"]),
                "is_validated": self.current_state["is_validated"],
                "session_complete": self.current_state["session_complete"],
                "known_facts": self.current_state["known_facts"],
                "original_problem": self.current_state["original_problem"],
                "previously_solved_questions": previously_solved,
                "current_question_solution": current_solution,
                "illustration_steps": self.current_state.get("illustration_steps", []),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting enhanced status: {str(e)}",
            }
