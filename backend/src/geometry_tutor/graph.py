"""
LangGraph workflow construction and routing for the Geometry Tutor system.
"""

import json
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from .core import GraphState
from .agents import (
    parse_problem,
    reason_and_solve,
    generate_hint,
    validate_solution,
    generate_solution,
    move_to_next_question,
    await_user_action,
)


def route_user_action(state: GraphState) -> str:
    """
    Routing function to determine the next node based on user action and state.
    """
    
    def display_detailed_status(state: GraphState) -> str:
        """Display detailed status information."""
        current_question_index = state.get("current_question_index", 0)
        questions = state.get("questions", [])
        hint_level = state.get("hint_level", 0)

        print("📊 TRẠNG THÁI CHI TIẾT:")
        print(f"  📍 Câu hỏi: {current_question_index + 1}/{len(questions)}")
        print(f"  💡 Gợi ý đã dùng: {hint_level}/3")
        print(f"  ✅ Đã xác thực: {'Có' if state.get('is_validated') else 'Chưa'}")
        if current_question_index < len(questions):
            print(f"  🎯 Câu hỏi: {questions[current_question_index]}")
        print()
        # Default fallback - this should handle cases where user_action is unexpected
        return "await_user_action"

    if state.get("error_message"):
        return END

    if state.get("session_complete"):
        return END

    user_action = state.get("user_action", "")

    # Initial routing after problem parsing
    if user_action == "start":
        return "reason_and_solve"

    # Route based on user's chosen action from input
    elif user_action == "1" or user_action.lower() == "hint":
        # Check if user has reached hint limit
        hint_level = state.get("hint_level", 0)
        if hint_level >= 3:
            print("⚠️  Bạn đã sử dụng hết 3 gợi ý cho câu hỏi này!")
            return "await_user_action"
        return "generate_hint"

    elif user_action == "2" or user_action.lower() == "submit":
        # Get user's solution input
        try:
            print("📝 Nhập lời giải của bạn:")
            solution = input("👤 Lời giải: ").strip()
            if solution:
                state["user_solution_attempt"] = solution
                return "validate_solution"
            else:
                print("❌ Lời giải không được để trống!")
                return "await_user_action"
        except Exception as e:
            print(f"❌ Lỗi khi nhập lời giải: {e}")
            return "await_user_action"

    elif user_action == "3" or user_action.lower() == "solution":
        return "generate_solution"

    elif user_action == "4" or user_action.lower() == "next":
        if state.get("is_validated"):
            return "move_to_next_question"
        else:
            print("❌ Cần hoàn thành câu hỏi hiện tại trước khi chuyển tiếp!")
            return "await_user_action"
    elif user_action == "5" or user_action.lower() == "status":
        # Display status and return to user input
        display_detailed_status(state)
        return "await_user_action"

    elif user_action == "6" or user_action.lower() == "exit":
        print("👋 Cảm ơn bạn đã sử dụng AI Geometry Tutor!")
        state["session_complete"] = True
        return END

    # Legacy routing for backward compatibility

    elif user_action == "hint":
        return "generate_hint"

    elif user_action == "validate":
        return "validate_solution"

    elif user_action == "solve":
        return "generate_solution"

    elif user_action == "next":
        return "move_to_next_question"

    else:
        if user_action:  # Only show error for non-empty input
            print("❌ Lựa chọn không hợp lệ! Vui lòng chọn từ 1-6.")
        return "await_user_action"


def should_continue_after_validation(state: GraphState) -> str:
    """
    Routing function after validation to determine if we should move to next question.
    """
    # Display the validation feedback
    if state.get("final_answer"):
        print("\\n" + "=" * 60)
        print("📝 KẾT QUẢ ĐÁNH GIÁ")
        print("=" * 60)
        print(state["final_answer"])
        print("=" * 60 + "\\n")

    if state.get("is_validated"):
        print("✅ Lời giải của bạn đã được xác nhận!")
        return "move_to_next_question"

    else:
        print("❌ Lời giải của bạn không chính xác. Vui lòng thử lại hoặc xin gợi ý.")
        return "await_user_action"


def should_continue_after_next_question(state: GraphState) -> str:
    """
    Routing function after moving to next question.
    """
    if state.get("session_complete"):
        return END
    else:
        return "reason_and_solve"


def create_geometry_tutor_graph() -> CompiledStateGraph:
    """
    Creates and compiles the LangGraph workflow for the Geometry Tutor.
    """

    # Create the graph
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("parse_problem", parse_problem)
    workflow.add_node("reason_and_solve", reason_and_solve)
    workflow.add_node("generate_hint", generate_hint)
    workflow.add_node("validate_solution", validate_solution)
    workflow.add_node("generate_solution", generate_solution)
    workflow.add_node("move_to_next_question", move_to_next_question)
    workflow.add_node("await_user_action", await_user_action)

    # Set entry point
    workflow.set_entry_point("parse_problem")

    # Add edges
    workflow.add_conditional_edges(
        "parse_problem",
        route_user_action,
        {
            "reason_and_solve": "reason_and_solve",
            "await_user_action": "await_user_action",
            END: END,
        },
    )
    workflow.add_edge("reason_and_solve", "await_user_action")
    workflow.add_conditional_edges(
        "await_user_action",
        route_user_action,
        {
            "generate_hint": "generate_hint",
            "validate_solution": "validate_solution",
            "generate_solution": "generate_solution",
            "move_to_next_question": "move_to_next_question",
            "await_user_action": "await_user_action",
            END: END,
        },
    )
    workflow.add_edge("generate_hint", "await_user_action")
    workflow.add_conditional_edges(
        "validate_solution",
        should_continue_after_validation,
        {
            "move_to_next_question": "move_to_next_question",
            "await_user_action": "await_user_action",
        },
    )
    workflow.add_edge("generate_solution", "move_to_next_question")
    workflow.add_conditional_edges(
        "move_to_next_question",
        should_continue_after_next_question,
        {"reason_and_solve": "reason_and_solve", END: END},
    )

    # Compile the graph
    return workflow.compile()
