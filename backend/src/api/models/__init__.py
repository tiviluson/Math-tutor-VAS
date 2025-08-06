"""
API models package for request and response data structures.
"""

from .requests import (
    ProblemRequest,
    ValidationRequest
)

from .responses import (
    SessionStatus,
    ApiResponse,
    HintResponse,
    ValidationResponse,
    SolutionResponse,
    IllustrationResponse
)

__all__ = [
    # Request models
    "ProblemRequest",
    "ValidationRequest",
    # Response models
    "SessionStatus",
    "ApiResponse",
    "HintResponse",
    "ValidationResponse",
    "SolutionResponse",
    "IllustrationResponse"
]