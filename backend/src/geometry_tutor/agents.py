"""
LangGraph node implementations (AI Agents) for the Geometry Tutor system.
"""

from typing import List, Dict

from .core import GraphState, format_facts_list
from .llm_utils import (
    initialize_llm,
    create_parsing_chain,
    create_reasoning_chain,
    create_validation_chain,
    create_input_classification_chain,
    create_question_extraction_chain,
)
from .prompts import prompt_templates, hint_builder


def parse_problem(state: GraphState) -> GraphState:
    """
    Node 1: parse_problem
    Agent: "Parsing Agent"
    Extracts structured information from the Vietnamese geometry problem.
    Uses LLM to separate problem statement from questions and extract facts and illustration steps.
    """
    llm = initialize_llm()
    if not llm:
        state["error_message"] = (
            "Không thể khởi tạo mô hình AI. Vui lòng kiểm tra cấu hình API."
        )
        return state

    try:
        # Create and use the parsing chain
        parsing_chain = create_parsing_chain(llm)
        parsed_data = parsing_chain.invoke({"problem": state["original_problem"]})

        # Use the separated problem statement from the LLM
        state["original_problem"] = parsed_data.problem_statement_only

        state["parsed_elements"] = {
            "points": parsed_data.points,
            "lines": parsed_data.lines,
            "shapes": parsed_data.shapes,
            "facts": parsed_data.given_facts,
        }

        state["questions"] = parsed_data.questions

        # Initialize known_facts and illustration_steps only with base problem facts
        # Question-specific facts and illustration steps will be added when needed
        state["known_facts"] = parsed_data.given_facts.copy()

        # Add base illustration steps from parsing
        illustration_steps = parsed_data.illustration_steps
        state["illustration_steps"] = (
            illustration_steps.copy() if illustration_steps else []
        )

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

        solver_prompt = prompt_templates.get_solver_prompt_template(
            current_question, all_available_facts, reasoning_chain, format_facts_list
        )

        try:
            # Create and use the reasoning chain
            reasoning_chain_processor = create_reasoning_chain(llm)
            step_data = reasoning_chain_processor.invoke(
                {"solver_prompt": solver_prompt}
            )
            print(step_data)

            reasoning_chain.append(
                {
                    "thought": step_data.thought,
                    "conclusion": step_data.conclusion,
                }
            )

            # Add new conclusion to AI discoveries (separate from user's known facts)
            conclusion = step_data.conclusion.strip()
            print(f"New AI discovery: {conclusion}")
            if conclusion and conclusion not in all_available_facts:
                ai_discoveries.append(conclusion)

            # Check if goal is reached
            if step_data.is_goal_reached or iteration >= max_iterations - 1:
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
    # AI discoveries are NOT merged here - only when question is solved/validated

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

    # Build hint prompt using the prompt builder
    hint_prompt = hint_builder.build_hint_prompt(
        new_hint_level,
        current_question,
        state["known_facts"],
        reasoning_chain,
        format_facts_list,
    )

    try:
        response = llm.invoke(hint_prompt)
        # Handle response content properly based on type
        if hasattr(response, "content"):
            if isinstance(response.content, str):
                hint_text = response.content.strip()
            else:
                hint_text = str(response.content)
        else:
            hint_text = str(response)
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
    Node 4: validate_solution (Enhanced)
    Agent: "Validation Agent"
    Handles different types of user input: questions, solutions, statements, etc.
    """
    llm = initialize_llm()
    if not llm:
        state["error_message"] = "Không thể khởi tạo mô hình AI."
        return state

    user_input = state["user_solution_attempt"]
    if not user_input.strip():
        state["error_message"] = "Nội dung đầu vào không được để trống."
        return state

    reasoning_chain = state["reasoning_chain"]
    current_question = state["questions"][state["current_question_index"]]
    known_facts = state["known_facts"]

    try:
        # Step 1: Classify the type of user input
        classification_prompt = prompt_templates.get_input_classification_prompt(
            current_question, user_input, known_facts, format_facts_list
        )

        classification_chain = create_input_classification_chain(llm)
        classification_result = classification_chain.invoke(
            {"classification_prompt": classification_prompt}
        )

        input_type = classification_result.input_type

        # Store the input type in state for API access
        state["user_input_type"] = input_type

        # Step 2: Handle based on input type
        if input_type == "question":
            # Handle student questions
            response_text = prompt_templates.get_question_answering_prompt(
                current_question,
                user_input,
                known_facts,
                reasoning_chain,
                format_facts_list,
            )

            # Generate direct response for questions (not using validation chain)
            response = llm.invoke(response_text)

            state["is_validated"] = False  # Questions don't mark as validated
            state["validation_score"] = 0  # Questions don't have a validation score
            state["final_answer"] = (
                f"**Câu trả lời cho câu hỏi của bạn:**\n\n{response.content}\n\n💡 Hãy thử áp dụng thông tin này để tiếp tục giải bài toán!"
            )

        elif input_type in ["complete_solution", "partial_solution", "statement"]:
            # Handle solutions and statements using enhanced validation
            validation_prompt = prompt_templates.get_validation_prompt_template(
                reasoning_chain, current_question, user_input
            )

            validation_chain = create_validation_chain(llm)
            validation_data = validation_chain.invoke(
                {"validation_prompt": validation_prompt}
            )

            state["is_validated"] = validation_data.is_correct

            feedback = validation_data.feedback
            score = validation_data.score

            # Store the score in state for API access
            state["validation_score"] = score

            state["final_answer"] = (
                f"**Kết quả đánh giá:**\n{feedback}\n\n**Mức độ hoàn thiện: {score}%**"
            )

            if state["is_validated"]:
                state["final_answer"] += "\n\n✅ Lời giải của bạn đã được chấp nhận!"

                # MERGE AI discoveries into known facts when solution is validated
                state = merge_ai_discoveries(state)

                # Add additional illustration steps when solution is validated
                additional_steps = validation_data.additional_illustration_steps
                if additional_steps:
                    state["illustration_steps"].extend(additional_steps)

        else:  # unclear or other types
            state["is_validated"] = False
            state["validation_score"] = (
                0  # Unclear inputs don't have a validation score
            )
            state["final_answer"] = (
                "**Thông tin chưa rõ ràng**\n\n"
                "Bạn có thể:\n"
                "- Đặt câu hỏi cụ thể về khái niệm hoặc phương pháp\n"
                "- Chia sẻ ý tưởng hoặc bước giải đã nghĩ ra\n"
                "- Trình bày lời giải hoàn chỉnh để được đánh giá\n\n"
                "💡 Hãy thử diễn đạt lại một cách rõ ràng hơn!"
            )

    except Exception as e:
        error_message = f"Lỗi trong quá trình xử lý: {str(e)}"
        state["error_message"] = error_message
        print(f"❌ {error_message}")

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

    solution_prompt = prompt_templates.get_solution_prompt(
        current_question, reasoning_chain
    )

    try:
        response = llm.invoke(solution_prompt)
        # Handle response content properly based on type
        if hasattr(response, "content"):
            if isinstance(response.content, str):
                state["final_answer"] = response.content.strip()
            else:
                state["final_answer"] = str(response.content)
        else:
            state["final_answer"] = str(response)

        # Display the generated solution immediately
        print("\n" + "=" * 60)
        print("📖 LỜI GIẢI HOÀN CHỈNH")
        print("=" * 60)
        print(state["final_answer"])
        print("=" * 60 + "\n")

        # MERGE AI discoveries into known facts when complete solution is provided
        state = merge_ai_discoveries(state)

    except Exception as e:
        state["final_answer"] = f"Lỗi khi tạo lời giải: {str(e)}"
        print(f"❌ {state['final_answer']}")

    return state


def move_to_next_question(state: GraphState) -> GraphState:
    """
    Node 6: move_to_next_question
    Standard function to advance to the next question and reset interaction state.
    Extracts new facts and illustration steps mentioned in the new question.
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

    # Extract new facts and illustration steps mentioned in the new question
    # This is separate from AI discoveries and should be done for each new question
    if state["current_question_index"] < len(state["questions"]):
        state = extract_question_facts_and_steps(state)

    # Note: known_facts and illustration_steps persist across questions
    # They may be updated when moving to next question if new facts/steps are mentioned
    # in the question itself, or when AI discoveries are merged after solving

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


def merge_ai_discoveries(state: GraphState) -> GraphState:
    """
    Helper function to merge AI discoveries into known facts.
    This ensures that facts discovered during reasoning are available for subsequent questions.
    """
    ai_discoveries = state.get("ai_discovered_facts", [])
    current_known = state["known_facts"]

    # Add AI discoveries to known facts (avoid duplicates)
    for discovery in ai_discoveries:
        if discovery and discovery not in current_known:
            current_known.append(discovery)

    state["known_facts"] = current_known
    # Clear AI discoveries since they're now part of known facts
    state["ai_discovered_facts"] = []

    return state


def extract_question_facts_and_steps(state: GraphState) -> GraphState:
    """
    Extract new facts and illustration steps mentioned in the current question.
    This is separate from AI discoveries and should be done when moving to a new question.
    Uses a proper LangChain with Pydantic output parser for reliable results.
    """
    llm = initialize_llm()
    if not llm:
        return state

    current_question_index = state["current_question_index"]
    if current_question_index >= len(state["questions"]):
        return state

    current_question = state["questions"][current_question_index]

    # Format current known facts and illustration steps for context
    known_facts_text = (
        format_facts_list(state["known_facts"])
        if state["known_facts"]
        else "Chưa có sự kiện nào"
    )
    illustration_steps_text = (
        format_facts_list(state["illustration_steps"])
        if state["illustration_steps"]
        else "Chưa có bước vẽ hình nào"
    )

    try:
        # Create and use the question extraction chain
        extraction_chain = create_question_extraction_chain(llm)
        extraction_data = extraction_chain.invoke(
            {
                "question": current_question,
                "known_facts": known_facts_text,
                "illustration_steps": illustration_steps_text,
            }
        )

        # Add new facts to known_facts (avoid duplicates)
        current_known = state["known_facts"]
        for fact in extraction_data.new_facts:
            if fact and fact.strip() and fact not in current_known:
                current_known.append(fact)

        # Add new illustration steps (avoid duplicates)
        current_steps = state["illustration_steps"]
        for step in extraction_data.new_illustration_steps:
            if step and step.strip() and step not in current_steps:
                current_steps.append(step)

    except Exception as e:
        # If extraction fails, log error but continue
        print(f"⚠️ Warning: Failed to extract facts from question: {str(e)}")
        pass

    return state
