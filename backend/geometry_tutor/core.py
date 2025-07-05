"""
Core data structures and state management for the AI Geometry Tutor system.
"""

from typing import List, Dict, Any
from typing_extensions import TypedDict


class GraphState(TypedDict):
    """
    Core state object for the AI Geometry Tutor system.
    Manages all data throughout the problem-solving workflow.
    """

    # --- Initial Problem Setup ---
    original_problem: str  # Raw text input from the user
    parsed_elements: Dict[str, Any]  # Structured representation of geometric givens
    # Example: {'points': ['A', 'B'], 'lines': [], 'facts': ['AB=5']}
    questions: List[str]  # Ordered list of questions from the problem

    # --- Dynamic Solver State ---
    current_question_index: int  # The index of the current question being addressed
    known_facts: List[str]  # A running list of givens (initial facts from problem)
    ai_discovered_facts: List[
        str
    ]  # Facts discovered by AI during reasoning (separate from user knowledge)
    reasoning_chain: List[Dict[str, str]]  # The agent's step-by-step solution path
    # Example: [{'thought': '...', 'conclusion': '...'}]

    # --- User Interaction State ---
    user_solution_attempt: str  # The user's most recent solution submission
    hint_level: int  # Counter for hints requested (0-3)
    generated_hints: List[str]  # The text of hints already provided to the user
    is_validated: bool  # Flag indicating if the user's solution was marked correct

    # --- Output State ---
    final_answer: str  # The complete, formatted solution for the current question
    error_message: str  # For communicating errors (e.g., parsing failure)

    # --- Control Flow ---
    user_action: str  # Current user action: 'hint', 'validate', 'solve', 'start'
    session_complete: bool  # Flag indicating if all questions are complete


def create_initial_state(problem: str) -> GraphState:
    """Create an initial state object for a new problem."""
    return GraphState(
        original_problem=problem,
        parsed_elements={},
        questions=[],
        current_question_index=0,
        known_facts=[],
        ai_discovered_facts=[],
        reasoning_chain=[],
        user_solution_attempt="",
        hint_level=0,
        generated_hints=[],
        is_validated=False,
        final_answer="",
        error_message="",
        user_action="start",
        session_complete=False,
    )


def format_facts_list(facts: List[str]) -> str:
    """Format a list of facts for display."""
    if not facts:
        return "Không có thông tin đã biết."
    return "\n".join(f"- {fact}" for fact in facts)


def get_combined_facts(state: GraphState) -> List[str]:
    """
    Get combined facts for AI reasoning: known_facts + ai_discovered_facts.
    This is used internally by AI agents but not shown to user.
    """
    known = state.get("known_facts", [])
    ai_discovered = state.get("ai_discovered_facts", [])
    return known + ai_discovered
