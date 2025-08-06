"""
Shared utilities and configuration for the AI Geometry Tutor.
"""

from .config import Settings, get_settings
from .logging import setup_logging
from .exceptions import TutorError, ConfigurationError

__all__ = [
    "Settings",
    "get_settings",
    "setup_logging",
    "TutorError",
    "ConfigurationError"
]