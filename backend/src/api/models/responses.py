"""
Pydantic models for API responses.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class SessionStatus(BaseModel):
    session_id: str
    success: bool
    current_question_index: int
    total_questions: int
    current_question: str
    hint_level: int
    hints_used: int
    is_validated: bool
    session_complete: bool
    known_facts: List[str]
    original_problem: str
    previously_solved_questions: List[Dict[str, Any]]
    current_question_solution: Optional[str] = None
    illustration_steps: List[str]
    created_at: datetime
    last_activity: datetime


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class HintResponse(BaseModel):
    success: bool
    hint_text: str
    hint_level: int
    max_hints_reached: bool


class ValidationResponse(BaseModel):
    success: bool = Field(..., description="Kết quả xử lý có thành công không")
    is_correct: bool = Field(
        ..., description="Nội dung có đúng không (false cho câu hỏi)"
    )
    feedback: str = Field(..., description="Phản hồi chi tiết cho học sinh")
    score: int = Field(..., description="Điểm số từ 0-100")
    moved_to_next: bool = Field(
        default=False, description="Đã chuyển sang câu tiếp theo chưa"
    )
    current_question_index: Optional[int] = Field(
        None, description="Chỉ số câu hỏi hiện tại"
    )
    session_complete: bool = Field(
        default=False, description="Phiên làm việc đã hoàn thành chưa"
    )
    input_type: Optional[str] = Field(
        None,
        description="Loại nội dung: question, complete_solution, partial_solution, statement, unclear",
    )
    message_type: Optional[str] = Field(
        None,
        description="Loại phản hồi: answer, validation_success, validation_feedback",
    )


class SolutionResponse(BaseModel):
    success: bool
    solution_text: str
    moved_to_next: bool = False
    current_question_index: Optional[int] = None
    session_complete: bool = False


class IllustrationResponse(BaseModel):
    success: bool
    message: str
    b64_string_viz: Optional[str] = Field(
        None, description="Base64 encoded visualization image"
    )
    error: Optional[str] = None