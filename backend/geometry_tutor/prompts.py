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
        return """Bạn là một chuyên gia hình học. Hãy đọc bài toán sau và thực hiện các nhiệm vụ:

1. Tách phần bài toán chính (problem_statement_only) KHÔNG bao gồm (các) câu hỏi
2. Trích xuất tất cả thông tin hình học (điểm, đường, hình)
3. Xác định các sự kiện đã cho từ phần bài toán chính
4. Xác định tất cả các câu hỏi riêng biệt theo thứ tự tuần tự
5. Mô tả các bước vẽ hình cần thiết cho bài toán chính

Yêu cầu quan trọng:
- problem_statement_only phải chứa chỉ phần mô tả bài toán, loại bỏ hoàn toàn các câu hỏi
- Các câu hỏi phải được sắp xếp theo thứ tự tuần tự đúng.
- Các câu hỏi phải được viết lại chính xác, không có sự thay đổi nào so với đề bài
- Các sự kiện (given_facts) và các bước vẽ hình (illustration_steps) CHỈ ĐẾN TỪ phần bài toán chính (problem_statement_only), không từ câu hỏi
- Các bước vẽ hình phải chi tiết, rõ ràng để học sinh có thể vẽ lại được
- Tất cả nội dung phải bằng tiếng Việt

Ví dụ 1:
Bài toán: Cho tam giác ABC vuông tại A có AB=3, AC=4. Gọi AH là đường cao của tam giác ABC (H là chân đường cao). a) Tính diện tích và chu vi của tam giác này. b) Chứng minh góc C < góc B. c) Tính độ dài đường trung tuyến AM của tam giác ABC.
Return {{
    "problem_statement_only": "Cho tam giác ABC vuông tại A có AB=3, AC=4. Gọi AH là đường cao của tam giác ABC (H là chân đường cao).",
    "points": ["A", "B", "C", "H"],
    "lines": ["AB", "AC", "BC", "AH"],
    "shapes": ["tam giác"],
    "given_facts": ["Tam giác ABC vuông tại A có AB=3, AC=4", "AH là đường cao của tam giác ABC", "H thuộc BC"],
    "questions": ["Tính diện tích và chu vi của tam giác này.", "Chứng minh góc C < góc B", "Tính độ dài đường trung tuyến AM của tam giác ABC."],
    "illustration_steps": ["Vẽ tam giác ABC vuông tại A có AB=3, AC=4", "Vẽ đường cao AH từ A đến BC", "Đánh dấu H là chân đường cao."]
}}

Bài toán: {problem}

{format_instructions}"""

    @staticmethod
    def get_reasoning_prompt() -> str:
        """Template for reasoning steps."""
        return """{solver_prompt}

{format_instructions}"""

    @staticmethod
    def get_solver_prompt_template(
        current_question: str,
        all_available_facts: List[str],
        reasoning_chain: List[Dict[str, Any]],
        format_facts_func,
    ) -> str:
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
    def get_validation_prompt_template(
        reasoning_chain: List[Dict[str, Any]], current_question: str, user_solution: str
    ) -> str:
        """Template for validation prompts."""
        return f"""Bạn là một trợ giảng dạy hình học thân thiện và xây dựng. Một chuỗi lập luận đúng là:

{json.dumps(reasoning_chain, ensure_ascii=False, indent=2)}

Học sinh đã nộp nội dung sau cho câu hỏi "{current_question}":

{user_solution}

Hãy phân tích nội dung học sinh vừa gửi và xác định loại tương tác:

1. **Nếu là câu hỏi**: Học sinh đang hỏi về khái niệm, phương pháp, hoặc cần giải thích thêm
   - Trả lời câu hỏi một cách rõ ràng và hữu ích
   - Kết nối câu trả lời với bài toán hiện tại
   - Hướng dẫn cách áp dụng vào bài toán cụ thể
   - Đặt is_correct = false để học sinh tiếp tục làm bài

2. **Nếu là lời giải hoàn chỉnh**: So sánh với chuỗi lập luận đúng
   - Đánh giá tính chính xác và logic
   - Khen ngợi những điểm đúng, chỉ ra điểm sai nếu có
   - Đặt is_correct = true nếu đúng, false nếu sai

3. **Nếu là lời giải một phần hoặc ý tưởng**: 
   - Đánh giá phần đã làm (đúng hay sai)
   - Khuyến khích và hướng dẫn bước tiếp theo
   - Gợi ý thêm để học sinh hoàn thiện
   - Đặt is_correct = false để học sinh tiếp tục

4. **Nếu là phát biểu/nhận xét**: Đánh giá tính đúng đắn và liên quan
   - Xác nhận nếu đúng, giải thích nếu sai
   - Liên kết với bài toán hiện tại
   - Hướng dẫn cách sử dụng thông tin này

Luôn luôn:
- Sử dụng giọng điệu khuyến khích, tích cực
- Đưa ra phản hồi xây dựng và hữu ích
- Khen ngợi nỗ lực của học sinh
- Hướng dẫn bước tiếp theo nếu cần

Nếu lời giải của học sinh đúng hoàn toàn, hãy đưa ra các bước vẽ hình bổ sung để minh họa cho lời giải này.

Trả về JSON với định dạng:
{{
    "is_correct": true/false,
    "feedback": "Phản hồi chi tiết, thân thiện và hỗ trợ cho học sinh",
    "score": 0-100,
    "additional_illustration_steps": ["Vẽ đường chéo AB", "AB cắt CD tại E", ...] (chỉ khi is_correct = true và có bước vẽ hình bổ sung. Nếu không thì trả về mảng rỗng)
}}"""

    @staticmethod
    def get_hint_prompt_conceptual(
        current_question: str,
        known_facts: List[str],
        reasoning_chain: List[Dict[str, Any]],
        format_facts_func,
    ) -> str:
        """Template for conceptual hints (level 1)."""
        return f"""Bạn là một giáo viên hình học. Học sinh đang giải câu hỏi: {current_question}

Các sự kiện học sinh đã biết:
{format_facts_func(known_facts)}

Chuỗi lập luận đúng là:
{json.dumps(reasoning_chain, ensure_ascii=False, indent=2)}

Hãy đưa ra gợi ý khái niệm tổng quát (không tiết lộ chi tiết cụ thể) về chiến lược giải quyết. 
Đặt câu hỏi hướng dẫn để học sinh tự suy nghĩ."""

    @staticmethod
    def get_hint_prompt_contextual(
        current_question: str,
        known_facts: List[str],
        reasoning_chain: List[Dict[str, Any]],
        format_facts_func,
    ) -> str:
        """Template for contextual hints (level 2)."""
        return f"""Bạn là một giáo viên hình học. Học sinh đang giải câu hỏi: {current_question}

Các sự kiện học sinh đã biết:
{format_facts_func(known_facts)}

Chuỗi lập luận đúng:
{json.dumps(reasoning_chain, ensure_ascii=False, indent=2)}

Hãy chỉ ra những sự kiện cụ thể từ danh sách đã biết mà học sinh cần chú ý để thực hiện bước tiếp theo.
Không tiết lộ bước lập luận, chỉ hướng dẫn tập trung vào thông tin nào."""

    @staticmethod
    def get_hint_prompt_direct(
        current_question: str,
        known_facts: List[str],
        reasoning_chain: List[Dict[str, Any]],
        format_facts_func,
    ) -> str:
        """Template for direct hints (level 3)."""
        return f"""Bạn là một giáo viên hình học. Học sinh đang giải câu hỏi: {current_question}

Các sự kiện học sinh đã biết:
{format_facts_func(known_facts)}

Chuỗi lập luận đúng:
{json.dumps(reasoning_chain, ensure_ascii=False, indent=2)}

Hãy gợi ý trực tiếp bước tiếp theo mà học sinh nên thực hiện, nhưng vẫn để học sinh tự hoàn thành.
Đưa ra một gợi ý cụ thể dưới dạng đề xuất."""

    @staticmethod
    def get_solution_prompt(
        current_question: str, reasoning_chain: List[Dict[str, Any]]
    ) -> str:
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

    @staticmethod
    def get_input_classification_prompt(
        current_question: str,
        user_input: str,
        known_facts: List[str],
        format_facts_func,
    ) -> str:
        """Template for classifying user input type (question, solution, statement, etc.)."""
        return f"""Bạn là một trợ giảng dạy hình học. Học sinh đang làm câu hỏi: {current_question}

Các sự kiện đã biết:
{format_facts_func(known_facts)}

Học sinh vừa gửi nội dung sau:
{user_input}

Hãy phân loại nội dung này và trả lời phù hợp:

Phân loại các loại đầu vào:
1. **question**: Câu hỏi về khái niệm, định nghĩa, phương pháp, hoặc yêu cầu giải thích
2. **complete_solution**: Lời giải hoàn chỉnh từ đầu đến cuối 
3. **partial_solution**: Lời giải một phần, ý tưởng, hoặc bước đầu
4. **statement**: Phát biểu, nhận xét, hoặc kết luận không có lời giải chi tiết
5. **unclear**: Nội dung không rõ ràng hoặc không liên quan

{{format_instructions}}"""

    @staticmethod
    def get_question_answering_prompt(
        current_question: str,
        user_question: str,
        known_facts: List[str],
        reasoning_chain: List[Dict[str, Any]],
        format_facts_func,
    ) -> str:
        """Template for answering student questions."""
        return f"""Bạn là một giáo viên hình học giàu kinh nghiệm và thân thiện. Học sinh đang làm câu hỏi: {current_question}

Các sự kiện đã biết:
{format_facts_func(known_facts)}

Chuỗi lập luận đúng (để tham khảo):
{json.dumps(reasoning_chain, ensure_ascii=False, indent=2)}

Học sinh hỏi: {user_question}

Hãy trả lời câu hỏi của học sinh một cách:
- Rõ ràng và dễ hiểu
- Liên kết với bài toán hiện tại
- Hướng dẫn cách áp dụng vào bài toán cụ thể
- Khuyến khích học sinh tiếp tục tự suy nghĩ
- Không tiết lộ hoàn toàn lời giải

Trả về phản hồi hướng dẫn và khuyến khích cho học sinh."""

    @staticmethod
    def get_question_extraction_prompt() -> str:
        """Template for extracting new facts and illustration steps from question text."""
        return """Bạn là một chuyên gia hình học. Hãy phân tích câu hỏi sau và trích xuất các thông tin mới (nếu có):

Câu hỏi: {question}

Các sự kiện đã biết:
{known_facts}

Các bước vẽ hình đã có:
{illustration_steps}

Nhiệm vụ:
1. Xác định các sự kiện mới được đề cập trong câu hỏi (ví dụ: "Gọi M là trung điểm AB", "Lấy điểm N trên đường thẳng CD", ...)
2. Xác định các bước vẽ hình mới được yêu cầu (ví dụ: "Vẽ đường tròn tâm O", "Nối AB", ...)

Yêu cầu:
- Chỉ trích xuất thông tin HOÀN TOÀN MỚI mà câu hỏi đề cập
- Các sự kiện mới (new_facts) KHÔNG được tương đương nhau. Nếu có lặp lại, hãy chỉ chọn trả về những sự kiện ngắn gọn hơn (ví dụ: ["Điểm M là trung điểm AB", "Điểm M là trung điểm AB"], chỉ trả về ["Điểm M là trung điểm AB"]; ["AB^2 = 25", "AB = 5"], chỉ trả về ["AB = 5"].)
- KHÔNG lặp lại thông tin đã có trong danh sách sự kiện đã biết hoặc bước vẽ hình đã có
- So sánh cẩn thận với danh sách hiện có để tránh trùng lặp
- Nếu không có thông tin mới, trả về mảng rỗng
- Thông tin phải rõ ràng và có thể sử dụng được

{format_instructions}"""


class HintPromptBuilder:
    """Builder for hint prompts based on hint level."""

    def __init__(self, prompts: PromptTemplates):
        self.prompts = prompts

    def build_hint_prompt(
        self,
        hint_level: int,
        current_question: str,
        known_facts: List[str],
        reasoning_chain: List[Dict[str, Any]],
        format_facts_func,
    ) -> str:
        """Build hint prompt based on hint level."""
        if hint_level == 1:
            return self.prompts.get_hint_prompt_conceptual(
                current_question, known_facts, reasoning_chain, format_facts_func
            )
        elif hint_level == 2:
            return self.prompts.get_hint_prompt_contextual(
                current_question, known_facts, reasoning_chain, format_facts_func
            )
        elif hint_level == 3:
            return self.prompts.get_hint_prompt_direct(
                current_question, known_facts, reasoning_chain, format_facts_func
            )
        else:
            raise ValueError(f"Invalid hint level: {hint_level}")


# Singleton instances for easy access
prompt_templates = PromptTemplates()
hint_builder = HintPromptBuilder(prompt_templates)
