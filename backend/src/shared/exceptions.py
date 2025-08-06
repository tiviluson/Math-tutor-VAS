"""
Shared exception classes for the AI Geometry Tutor.
"""


class TutorError(Exception):
    """Base exception for tutor-related errors."""
    
    def __init__(self, message: str, code: str = "TUTOR_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class ConfigurationError(TutorError):
    """Exception for configuration-related errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "CONFIGURATION_ERROR")


class SessionError(TutorError):
    """Exception for session-related errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "SESSION_ERROR")


class LLMError(TutorError):
    """Exception for LLM-related errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "LLM_ERROR")


class ValidationError(TutorError):
    """Exception for validation-related errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class VisualizationError(TutorError):
    """Exception for visualization-related errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "VISUALIZATION_ERROR")