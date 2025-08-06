"""
API middleware package for cross-cutting concerns.
"""

from .error_handling import setup_error_handlers
from .logging import setup_request_logging
from .cors import setup_cors

__all__ = [
    "setup_error_handlers",
    "setup_request_logging",
    "setup_cors"
]