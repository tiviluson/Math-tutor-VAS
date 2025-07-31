"""
API models package for request and response data structures.
"""

from .requests import (
    ProblemRequest,
    ValidationRequest,
    SessionRequest
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
    "SessionRequest",
    # Response models
    "SessionStatus",
    "ApiResponse",
    "HintResponse",
    "ValidationResponse",
    "SolutionResponse",
    "IllustrationResponse"
]