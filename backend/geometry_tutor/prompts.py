"""
Prompt templates for the AI Geometry Tutor system.
All prompt templates are centralized here for better maintainability.
"""

from typing import Dict, List, Any
import json


class PromptTemplates:
    """Container for all prompt templates used in the geometry tutor system."""
    
    @staticmethod
    def get_parsing_prompt() -> str:
        """Template for parsing geometry problems."""
        return """Bạn là một chuyên gia hình học. Hãy đọc bài toán sau và trích xuất tất cả thông tin hình học, 
các sự kiện đã cho, các câu hỏi riêng biệt, và các bước vẽ hình.

Các câu hỏi phải được sắp xếp theo thứ tự tuần tự đúng.
Các câu hỏi phải được viết lại chính xác, không có sự thay đổi nào so với đề bài.
Cả các sự kiện đã cho và câu hỏi phải được viết bằng tiếng Việt.
Các bước vẽ hình phải được mô tả chi tiết, rõ ràng để học sinh có thể vẽ lại được.

Bài toán: {problem}

{format_instructions}"""

    @staticmethod
    def get_reasoning_prompt() -> str:
        """Template for reasoning steps."""
        return """{solver_prompt}

{format_instructions}"""

    @staticmethod
    def get_solver_prompt_template(current_question: str, all_available_facts: List[str], reasoning_chain: List[Dict[str, Any]], format_facts_func) -> str:
        """Template for solver reasoning prompts."""
        return f"""Bạn là một chuyên gia giải toán hình học. Mục tiêu của bạn là chứng minh/giải quyết: {current_question}

Bạn đã biết các sự kiện sau:
{format_facts_func(all_available_facts)}

Bước lập luận đã thực hiện:
{json.dumps(reasoning_chain, ensure_ascii=False, indent=2) if reasoning_chain else "Chưa có bước nào"}

Hãy xác định bước logic tiếp theo để đạt được mục tiêu. Trả về JSON với định dạng:
{{
    "thought": "Suy nghĩ logic cho bước này, bao gồm lập luận chi tiết",
    "conclusion": "Kết luận cụ thể từ bước này. Chỉ bao gồm kết luận cuối cùng, không cần lập luận",
    "is_goal_reached": true/false
}}

Nếu kết luận đã đạt được mục tiêu (trả lời được câu hỏi), hãy đặt is_goal_reached = true."""

    @staticmethod
    def get_validation_prompt() -> str:
        """Template for validation."""
        return """{validation_prompt}

{format_instructions}"""

    @staticmethod
    def get_validation_prompt_template(reasoning_chain: List[Dict[str, Any]], current_question: str, user_solution: str) -> str:
        """Template for validation prompts."""
        return f"""Bạn là một trợ giảng dạy hình học. Một chuỗi lập luận đúng là:

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
}}"""

    @staticmethod
    def get_hint_prompt_conceptual(current_question: str, known_facts: List[str], reasoning_chain: List[Dict[str, Any]], format_facts_func) -> str:
        """Template for conceptual hints (level 1)."""
        return f"""Bạn là một giáo viên hình học. Học sinh đang giải câu hỏi: {current_question}

Các sự kiện học sinh đã biết:
{format_facts_func(known_facts)}

Chuỗi lập luận đúng là:
{json.dumps(reasoning_chain, ensure_ascii=False, indent=2)}

Hãy đưa ra gợi ý khái niệm tổng quát (không tiết lộ chi tiết cụ thể) về chiến lược giải quyết. 
Đặt câu hỏi hướng dẫn để học sinh tự suy nghĩ."""

    @staticmethod
    def get_hint_prompt_contextual(current_question: str, known_facts: List[str], reasoning_chain: List[Dict[str, Any]], format_facts_func) -> str:
        """Template for contextual hints (level 2)."""
        return f"""Bạn là một giáo viên hình học. Học sinh đang giải câu hỏi: {current_question}

Các sự kiện học sinh đã biết:
{format_facts_func(known_facts)}

Chuỗi lập luận đúng:
{json.dumps(reasoning_chain, ensure_ascii=False, indent=2)}

Hãy chỉ ra những sự kiện cụ thể từ danh sách đã biết mà học sinh cần chú ý để thực hiện bước tiếp theo.
Không tiết lộ bước lập luận, chỉ hướng dẫn tập trung vào thông tin nào."""

    @staticmethod
    def get_hint_prompt_direct(current_question: str, known_facts: List[str], reasoning_chain: List[Dict[str, Any]], format_facts_func) -> str:
        """Template for direct hints (level 3)."""
        return f"""Bạn là một giáo viên hình học. Học sinh đang giải câu hỏi: {current_question}

Các sự kiện học sinh đã biết:
{format_facts_func(known_facts)}

Chuỗi lập luận đúng:
{json.dumps(reasoning_chain, ensure_ascii=False, indent=2)}

Hãy gợi ý trực tiếp bước tiếp theo mà học sinh nên thực hiện, nhưng vẫn để học sinh tự hoàn thành.
Đưa ra một gợi ý cụ thể dưới dạng đề xuất."""

    @staticmethod
    def get_solution_prompt(current_question: str, reasoning_chain: List[Dict[str, Any]]) -> str:
        """Template for solution generation."""
        return f"""Bạn là một giáo viên hình học. Hãy viết một lời giải rõ ràng, từng bước dựa trên chuỗi logic sau.
Giải thích mỗi bước một cách rõ ràng bằng tiếng Việt.

Câu hỏi: {current_question}

Chuỗi lập luận:
{json.dumps(reasoning_chain, ensure_ascii=False, indent=2)}

Hãy viết lời giải hoàn chỉnh với định dạng:
- Đầu tiên nêu rõ điều cần chứng minh/tính toán
- Từng bước giải thích chi tiết
- Kết luận cuối cùng

Sử dụng định dạng Markdown để làm đẹp lời giải."""

    @staticmethod
    def get_text_extraction_prompt() -> str:
        """Template for text extraction from images."""
        return """{extraction_prompt}

{format_instructions}"""

    @staticmethod
    def get_image_analysis_prompt() -> str:
        """Template for analyzing images and extracting problem text."""
        return """Bạn là một chuyên gia toán học, hãy phân tích hình ảnh bài toán hình học này và trích xuất thông tin.

Hãy thực hiện các nhiệm vụ sau:
1. Trích xuất toàn bộ văn bản của bài toán (nếu có) trong hình ảnh
2. Mô tả chi tiết hình vẽ/minh họa trong bài toán (nếu có)

Trả về kết quả theo định dạng JSON:
{{
    "problem_text": "Văn bản bài toán đầy đủ đã được trích xuất từ hình ảnh",
    "illustration_description": "Mô tả chi tiết hình vẽ nếu có, ngược lại trả về chuỗi rỗng",
    "has_text_in_image": true/false
}}

Yêu cầu:
- Trích xuất chính xác toàn bộ văn bản trong hình ảnh
- Mô tả chi tiết các yếu tố hình học (điểm, đường, góc, hình dạng, v.v...)  
- Đảm bảo văn bản tiếng Việt chính xác
- Nếu không có văn bản trong hình ảnh, trả về chuỗi rỗng cho problem_text
- Nếu không có hình vẽ minh họa, trả về chuỗi rỗng cho illustration_description

{format_instructions}"""


class HintPromptBuilder:
    """Builder for hint prompts based on hint level."""
    
    def __init__(self, prompts: PromptTemplates):
        self.prompts = prompts
    
    def build_hint_prompt(self, hint_level: int, current_question: str, known_facts: List[str], reasoning_chain: List[Dict[str, Any]], format_facts_func) -> str:
        """Build hint prompt based on hint level."""
        if hint_level == 1:
            return self.prompts.get_hint_prompt_conceptual(current_question, known_facts, reasoning_chain, format_facts_func)
        elif hint_level == 2:
            return self.prompts.get_hint_prompt_contextual(current_question, known_facts, reasoning_chain, format_facts_func)
        elif hint_level == 3:
            return self.prompts.get_hint_prompt_direct(current_question, known_facts, reasoning_chain, format_facts_func)
        else:
            raise ValueError(f"Invalid hint level: {hint_level}")


# Singleton instances for easy access
prompt_templates = PromptTemplates()
hint_builder = HintPromptBuilder(prompt_templates)
