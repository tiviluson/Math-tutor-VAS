"""
Consolidated GeometryTutor module.
Provides both interactive and API-compatible tutor implementations.
"""

# Import the main classes for backward compatibility
from .base_tutor import BaseGeometryTutor
from .interactive_tutor import InteractiveGeometryTutor, create_tutor

# For backward compatibility, make InteractiveGeometryTutor available as GeometryTutor
GeometryTutor = InteractiveGeometryTutor

__all__ = [
    "BaseGeometryTutor",
    "GeometryTutor", 
    "InteractiveGeometryTutor",
    "create_tutor"
]