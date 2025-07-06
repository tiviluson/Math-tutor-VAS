"""
AI Geometry Tutor for Vietnamese High School Students

This package implements an AI-powered Geometry Tutor system using LangGraph 
and LLM-native reasoning designed for Vietnamese high school students.
"""

from .tutor import GeometryTutor
from .core import GraphState, create_initial_state

__version__ = "0.1.0"
__all__ = ["GeometryTutor", "GraphState", "create_initial_state"]
