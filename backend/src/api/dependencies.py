"""
FastAPI dependencies for dependency injection.
Provides singleton instances of services for API endpoints.
"""

from functools import lru_cache
from fastapi import HTTPException

from src.services.session_service import SessionService
from src.services.tutor_service import TutorService
from src.services.visualization_service import VisualizationService
from src.services.llm_service import LLMService
from src.geometry_tutor.llm_utils import setup_environment


@lru_cache()
def get_llm_service() -> LLMService:
    """Get singleton LLM service instance."""
    try:
        return LLMService()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize LLM service: {str(e)}"
        )


@lru_cache()
def get_session_service() -> SessionService:
    """Get singleton session service instance."""
    return SessionService()


@lru_cache()
def get_tutor_service() -> TutorService:
    """Get singleton tutor service instance."""
    try:
        llm_service = get_llm_service()
        return TutorService(llm_service)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize tutor service: {str(e)}"
        )


@lru_cache() 
def get_visualization_service() -> VisualizationService:
    """Get singleton visualization service instance."""
    return VisualizationService()


def check_environment():
    """Dependency to ensure environment is properly set up."""
    if not setup_environment():
        raise HTTPException(
            status_code=500,
            detail="Environment setup failed. Please check API key configuration.",
        )