"""
LangGraph node implementations (AI Agents) for the Geometry Tutor system.
"""

import json
from typing import List, Dict

from .core import GraphState, format_facts_list
from .llm_utils import initialize_llm, safe_json_parse


def parse_problem(state: GraphState) -> GraphState:
    """
    Node 1: parse_problem
    Agent: "Parsing Agent"
    Extracts structured information from the Vietnamese geometry problem.
    """
    llm = initialize_llm()
    if not llm:
        state["error_message"] = (
            "Không thể khởi tạo mô hình AI. Vui lòng kiểm tra cấu hình API."
        )
        return state

    parsing_prompt = f"""
Bạn là một chuyên gia hình học. Hãy đọc bài toán sau và trích xuất tất cả thông tin hình học, 
các sự kiện đã cho, các câu hỏi riêng biệt, và các bước vẽ hình thành định dạng JSON.

Các câu hỏi phải được sắp xếp theo thứ tự tuần tự đúng.
Các câu hỏi phải được viết lại chính xác, không có sự thay đổi nào so với đề bài.
Cả các sự kiện đã cho và câu hỏi phải được viết bằng tiếng Việt.
Các bước vẽ hình phải được mô tả chi tiết, rõ ràng để học sinh có thể vẽ lại được.

Bài toán: {state['original_problem']}

Vui lòng trả về JSON với định dạng sau:
{{
    "points": ["A", "B", "C", ...],
    "lines": ["AB", "BC", ...],
    "shapes": ["triangle ABC", "circle O", ...],
    "given_facts": ["AB = 5", "góc ABC = 90°", ...],
    "questions": ["Chứng minh tam giác ABC vuông", "Tính diện tích tam giác", ...],
    "illustration_steps": ["Vẽ đường tròn tâm O, bán kính R", "Lấy điểm A trên đường thẳng qua O", ...]
}}
"""

    try:
        response = llm.invoke(parsing_prompt)
        parsed_data = safe_json_parse(
            response.content,
            {
                "points": [],
                "lines": [],
                "shapes": [],
                "given_facts": [],
                "questions": [],
                "illustration_steps": [],
            },
        )

        state["parsed_elements"] = {
            "points": parsed_data.get("points", []),
            "lines": parsed_data.get("lines", []),
            "shapes": parsed_data.get("shapes", []),
            "facts": parsed_data.get("given_facts", []),
        }

        state["questions"] = parsed_data.get("questions", [])
        state["known_facts"] = parsed_data.get("given_facts", []).copy()

        # Add illustration steps from parsing
        illustration_steps = parsed_data.get("illustration_steps", [])
        state["illustration_steps"].extend(illustration_steps)

        if not state["questions"]:
            state["error_message"] = (
                "Không thể phân tích các câu hỏi từ bài toán. Vui lòng kiểm tra lại đề bài."
            )
        else:
            state["error_message"] = ""

    except Exception as e:
        state["error_message"] = f"Lỗi khi phân tích bài toán: {str(e)}"

    return state


def reason_and_solve(state: GraphState) -> GraphState:
    """
    Node 2: reason_and_solve
    Agent: "Solver Agent"
    Develops a step-by-step solution for the current question using iterative reasoning.
    AI discoveries are kept separate from user's known facts until solution is validated.
    """
    llm = initialize_llm()
    if not llm:
        state["error_message"] = "Không thể khởi tạo mô hình AI."
        return state

    if state["current_question_index"] >= len(state["questions"]):
        state["session_complete"] = True
        return state

    current_question = state["questions"][state["current_question_index"]]
    # Use only the base known facts (from problem) + any previously validated AI discoveries
    base_facts = state["known_facts"]
    ai_discoveries = []  # Fresh AI discoveries for this reasoning session
    reasoning_chain = []

    max_iterations = 10  # Prevent infinite loops
    iteration = 0

    while iteration < max_iterations:
        # Combine base facts with current AI discoveries for reasoning
        all_available_facts = base_facts + ai_discoveries

        solver_prompt = f"""
Bạn là một chuyên gia giải toán hình học. Mục tiêu của bạn là chứng minh/giải quyết: {current_question}

Bạn đã biết các sự kiện sau:
{format_facts_list(all_available_facts)}

Bước lập luận đã thực hiện:
{json.dumps(reasoning_chain, ensure_ascii=False, indent=2) if reasoning_chain else "Chưa có bước nào"}

Hãy xác định bước logic tiếp theo để đạt được mục tiêu. Trả về JSON với định dạng:
{{
    "thought": "Suy nghĩ logic cho bước này, bao gồm lập luận chi tiết",
    "conclusion": "Kết luận cụ thể từ bước này. Chỉ bao gồm kết luận cuối cùng, không cần lập luận",
    "is_goal_reached": true/false
}}

Nếu kết luận đã đạt được mục tiêu (trả lời được câu hỏi), hãy đặt is_goal_reached = true.
"""

        try:
            response = llm.invoke(solver_prompt)
            step_data = safe_json_parse(
                response.content,
                {
                    "thought": "Không thể phân tích bước này",
                    "conclusion": "",
                    "is_goal_reached": False,
                },
            )

            reasoning_chain.append(
                {
                    "thought": step_data.get("thought", ""),
                    "conclusion": step_data.get("conclusion", ""),
                }
            )

            # Add new conclusion to AI discoveries (separate from user's known facts)
            conclusion = step_data.get("conclusion", "").strip()
            if conclusion and conclusion not in all_available_facts:
                ai_discoveries.append(conclusion)

            # Check if goal is reached
            if (
                step_data.get("is_goal_reached", False)
                or iteration >= max_iterations - 1
            ):
                break

        except Exception as e:
            reasoning_chain.append(
                {
                    "thought": f"Lỗi trong quá trình lập luận: {str(e)}",
                    "conclusion": "Không thể tiếp tục lập luận",
                }
            )
            break

        iteration += 1

    # Store the reasoning chain and AI discoveries separately
    state["reasoning_chain"] = reasoning_chain
    state["ai_discovered_facts"] = ai_discoveries
    # known_facts remains unchanged - only contains original problem facts

    return state


def generate_hint(state: GraphState) -> GraphState:
    """
    Node 3: generate_hint
    Agent: "Hinting Agent"
    Provides scaffolded hints based on the AI's solution path.
    """
    llm = initialize_llm()
    if not llm:
        state["error_message"] = "Không thể khởi tạo mô hình AI."
        return state

    reasoning_chain = state["reasoning_chain"]
    hint_level = state["hint_level"]
    current_question = state["questions"][state["current_question_index"]]

    if hint_level >= 3:
        state["generated_hints"].append(
            "Bạn đã sử dụng hết số lần gợi ý. Hãy thử giải hoặc xem đáp án."
        )
        return state

    # Increment hint level
    state["hint_level"] = hint_level + 1
    new_hint_level = state["hint_level"]

    if new_hint_level == 1:
        # Hint 1: Conceptual - General strategy
        hint_prompt = f"""
Bạn là một giáo viên hình học. Học sinh đang giải câu hỏi: {current_question}

Các sự kiện học sinh đã biết:
{format_facts_list(state["known_facts"])}

Chuỗi lập luận đúng là:
{json.dumps(reasoning_chain, ensure_ascii=False, indent=2)}

Hãy đưa ra gợi ý khái niệm tổng quát (không tiết lộ chi tiết cụ thể) về chiến lược giải quyết. 
Đặt câu hỏi hướng dẫn để học sinh tự suy nghĩ.
"""

    elif new_hint_level == 2:
        # Hint 2: Contextual - Point to specific facts
        # Use only user's known facts for hints, not AI discoveries
        hint_prompt = f"""
Bạn là một giáo viên hình học. Học sinh đang giải câu hỏi: {current_question}

Các sự kiện học sinh đã biết:
{format_facts_list(state["known_facts"])}

Chuỗi lập luận đúng:
{json.dumps(reasoning_chain, ensure_ascii=False, indent=2)}

Hãy chỉ ra những sự kiện cụ thể từ danh sách đã biết mà học sinh cần chú ý để thực hiện bước tiếp theo.
Không tiết lộ bước lập luận, chỉ hướng dẫn tập trung vào thông tin nào.
"""

    else:  # hint_level == 3
        # Hint 3: Direct - Next step suggestion
        hint_prompt = f"""
Bạn là một giáo viên hình học. Học sinh đang giải câu hỏi: {current_question}

Các sự kiện học sinh đã biết:
{format_facts_list(state["known_facts"])}

Chuỗi lập luận đúng:
{json.dumps(reasoning_chain, ensure_ascii=False, indent=2)}

Hãy gợi ý trực tiếp bước tiếp theo mà học sinh nên thực hiện, nhưng vẫn để học sinh tự hoàn thành.
Đưa ra một gợi ý cụ thể dưới dạng đề xuất.
"""

    try:
        response = llm.invoke(hint_prompt)
        hint_text = response.content.strip()
        state["generated_hints"].append(hint_text)

        # Display the generated hint immediately
        print("\n" + "=" * 60)
        print(f"💡 GỢI Ý LẦN {new_hint_level}")
        print("=" * 60)
        print(hint_text)
        print("=" * 60 + "\n")

    except Exception as e:
        error_message = f"Lỗi khi tạo gợi ý: {str(e)}"
        state["generated_hints"].append(error_message)
        print(f"❌ {error_message}")

    return state


def validate_solution(state: GraphState) -> GraphState:
    """
    Node 4: validate_solution
    Agent: "Validation Agent"
    Compares student solution with the correct reasoning path.
    """
    llm = initialize_llm()
    if not llm:
        state["error_message"] = "Không thể khởi tạo mô hình AI."
        return state

    user_solution = state["user_solution_attempt"]
    reasoning_chain = state["reasoning_chain"]
    current_question = state["questions"][state["current_question_index"]]

    validation_prompt = f"""
Bạn là một trợ giảng dạy hình học. Một chuỗi lập luận đúng là:

{json.dumps(reasoning_chain, ensure_ascii=False, indent=2)}

Học sinh đã nộp lời giải sau cho câu hỏi "{current_question}":

{user_solution}

Hãy so sánh lập luận của học sinh với đường lối giải đúng. Lập luận của học sinh có hợp lý không?

Nếu đúng, hãy khen ngợi và xác nhận. Nếu sai, hãy nhẹ nhàng giải thích điểm sai hoặc những gì học sinh còn thiếu.

Nếu lời giải của học sinh đúng, hãy đưa ra các bước vẽ hình bổ sung để minh họa cho lời giải này.

Trả về JSON với định dạng:
{{
    "is_correct": true/false,
    "feedback": "Phản hồi chi tiết cho học sinh",
    "score": 0-100,
    "additional_illustration_steps": ["Vẽ đường chéo AB", "AB cắt CD tại E", ...] (chỉ khi is_correct = true và có bước vẽ hình bổ sung. Nếu không thì trả về mảng rỗng)
}}
"""

    try:
        response = llm.invoke(validation_prompt)
        validation_data = safe_json_parse(
            response.content,
            {
                "is_correct": False,
                "feedback": "Không thể đánh giá lời giải",
                "score": 0,
                "additional_illustration_steps": [],
            },
        )

        state["is_validated"] = validation_data.get("is_correct", False)

        # Store validation feedback
        feedback = validation_data.get("feedback", "Không có phản hồi")
        score = validation_data.get("score", 0)

        state["final_answer"] = (
            f"**Kết quả đánh giá:**\n{feedback}\n\n**Điểm: {score}/100**"
        )

        if state["is_validated"]:
            state["final_answer"] += "\n\n✅ Lời giải của bạn đã được chấp nhận!"

            # MERGE AI discoveries into known facts when solution is validated
            ai_discoveries = state.get("ai_discovered_facts", [])
            current_known = state["known_facts"]

            # Add AI discoveries to known facts (avoid duplicates)
            for discovery in ai_discoveries:
                if discovery and discovery not in current_known:
                    current_known.append(discovery)

            state["known_facts"] = current_known
            # Clear AI discoveries since they're now part of known facts
            state["ai_discovered_facts"] = []

            # Add additional illustration steps when solution is validated
            additional_steps = validation_data.get("additional_illustration_steps", [])
            if additional_steps:
                state["illustration_steps"].extend(additional_steps)

    except Exception as e:
        state["final_answer"] = f"Lỗi khi đánh giá lời giải: {str(e)}"
        state["is_validated"] = False

    return state


def generate_solution(state: GraphState) -> GraphState:
    """
    Node 5: generate_solution
    Agent: "Solution Generation Agent"
    Transforms the structured reasoning into a formatted final answer.
    """
    llm = initialize_llm()
    if not llm:
        state["error_message"] = "Không thể khởi tạo mô hình AI."
        return state

    reasoning_chain = state["reasoning_chain"]
    current_question = state["questions"][state["current_question_index"]]

    solution_prompt = f"""
Bạn là một giáo viên hình học. Hãy viết một lời giải rõ ràng, từng bước dựa trên chuỗi logic sau.
Giải thích mỗi bước một cách rõ ràng bằng tiếng Việt.

Câu hỏi: {current_question}

Chuỗi lập luận:
{json.dumps(reasoning_chain, ensure_ascii=False, indent=2)}

Hãy viết lời giải hoàn chỉnh với định dạng:
- Đầu tiên nêu rõ điều cần chứng minh/tính toán
- Từng bước giải thích chi tiết
- Kết luận cuối cùng

Sử dụng định dạng Markdown để làm đẹp lời giải.
"""

    try:
        response = llm.invoke(solution_prompt)
        state["final_answer"] = response.content.strip()

        # Display the generated solution immediately
        print("\n" + "=" * 60)
        print("📖 LỜI GIẢI HOÀN CHỈNH")
        print("=" * 60)
        print(state["final_answer"])
        print("=" * 60 + "\n")

        # MERGE AI discoveries into known facts when complete solution is provided
        ai_discoveries = state.get("ai_discovered_facts", [])
        current_known = state["known_facts"]

        # Add AI discoveries to known facts (avoid duplicates)
        for discovery in ai_discoveries:
            if discovery and discovery not in current_known:
                current_known.append(discovery)

        state["known_facts"] = current_known
        # Clear AI discoveries since they're now part of known facts
        state["ai_discovered_facts"] = []

    except Exception as e:
        state["final_answer"] = f"Lỗi khi tạo lời giải: {str(e)}"
        print(f"❌ {state['final_answer']}")

    return state


def move_to_next_question(state: GraphState) -> GraphState:
    """
    Node 6: move_to_next_question
    Standard function to advance to the next question and reset interaction state.
    """
    # Increment question index
    state["current_question_index"] += 1

    # Reset interaction-specific state
    state["hint_level"] = 0
    state["generated_hints"] = []
    state["is_validated"] = False
    state["user_solution_attempt"] = ""
    state["final_answer"] = ""
    state["reasoning_chain"] = []
    state["ai_discovered_facts"] = []  # Reset AI discoveries for new question

    # Check if all questions are complete
    if state["current_question_index"] >= len(state["questions"]):
        state["session_complete"] = True
        completion_message = (
            "🎉 **Chúc mừng!** Bạn đã hoàn thành tất cả câu hỏi trong bài toán này!"
        )
        state["final_answer"] = completion_message

        # Display completion message immediately
        print("\n" + "=" * 60)
        print("🎉 HOÀN THÀNH BÀI TOÁN")
        print("=" * 60)
        print(completion_message)
        print("=" * 60 + "\n")

    # known_facts persists across questions
    return state


def await_user_action(state: GraphState) -> GraphState:
    """
    Active node that handles user input directly within the graph flow.
    Displays current question and prompts for user action.
    """

    def display_question_and_status(state: GraphState) -> None:
        """Display the current question and available user actions."""
        current_question_index = state.get("current_question_index", 0)
        questions = state.get("questions", [])

        if current_question_index >= len(questions):
            print("🎉 Đã hoàn thành tất cả câu hỏi!")
            return

        current_question = questions[current_question_index]
        hint_level = state.get("hint_level", 0)
        generated_hints = state.get("generated_hints", [])

        print("=" * 60)
        print(f"📋 CÂU HỎI {current_question_index + 1}/{len(questions)}")
        print("=" * 60)
        print(f"❓ {current_question}")
        print()

        # Show current status - only user's known facts
        if state.get("known_facts"):
            print("📝 Các sự kiện đã biết:")
            for i, fact in enumerate(state["known_facts"], 1):
                print(f"  {i}. {fact}")
            print()

        # Show hints if any have been generated
        if generated_hints:
            print("💡 Gợi ý đã nhận:")
            for i, hint in enumerate(generated_hints, 1):
                print(f"\n📌 Gợi ý {i}:")
                print(f"  {hint}")
            print()

        # Show available actions
        print("🎯 Các hành động có thể thực hiện:")
        print("  1. 💡 Xin gợi ý (hint)")
        print("  2. 📝 Nộp lời giải (submit)")
        print("  3. 📖 Xem đáp án (solution)")
        if state.get("is_validated"):
            print("  4. ➡️  Câu hỏi tiếp theo (next)")
        print("  5. 📊 Xem trạng thái (status)")
        print("  6. 🚪 Thoát (exit)")
        print()

    def get_user_input_in_node() -> str:
        """Get user input for the current action within the graph node."""
        try:
            user_choice = input("👤 Chọn hành động (1-6): ").strip()
            return user_choice
        except KeyboardInterrupt:
            print("\n👋 Thoát chương trình...")
            return "6"  # Exit
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return ""

    current_question_index = state.get("current_question_index", 0)
    questions = state.get("questions", [])

    if current_question_index >= len(questions):
        state["session_complete"] = True
        return state

    # Display current question and status
    display_question_and_status(state)

    # Get user input directly
    user_choice = get_user_input_in_node()

    # Store user choice in state for routing
    state["user_action"] = user_choice

    return state
