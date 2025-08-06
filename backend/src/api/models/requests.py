"""
Pydantic models for API requests.
"""

from typing import Optional
from pydantic import BaseModel, Field


class ProblemRequest(BaseModel):
    problem_text: str = Field(
        default="",
        description="Vietnamese geometry problem text (required if is_img=false)",
    )
    is_img: bool = Field(
        default=False,
        description="Whether the request includes an image instead of text",
    )
    img: Optional[str] = Field(
        default=None,
        description="Base64 encoded image of the geometry problem (required if is_img=true)",
    )


class ValidationRequest(BaseModel):
    session_id: str = Field(..., description="Session ID from problem creation")
    # action: str = Field(
    #     ..., description="Action to perform: hint, submit, solution, next"
    # )
    user_input: Optional[str] = Field(
        None, description="Solution text for submit action"
    )


