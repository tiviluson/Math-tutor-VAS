"""
FastAPI dependencies for dependency injection.
Provides singleton instances of services for API endpoints.
"""

from fastapi import HTTPException

from src.services.session_service import SessionService
from src.services.tutor_service import TutorService
from src.services.visualization_service import VisualizationService
from src.services.llm_service import LLMService
from src.geometry_tutor.llm_utils import setup_environment

# Global singleton instances
_llm_service = None
_session_service = None
_tutor_service = None
_visualization_service = None


def get_llm_service() -> LLMService:
    """Get singleton LLM service instance."""
    global _llm_service
    if _llm_service is None:
        try:
            _llm_service = LLMService()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize LLM service: {str(e)}"
            )
    return _llm_service


def get_session_service() -> SessionService:
    """Get singleton session service instance."""
    global _session_service
    if _session_service is None:
        _session_service = SessionService()
    return _session_service


def get_tutor_service() -> TutorService:
    """Get singleton tutor service instance."""
    global _tutor_service
    if _tutor_service is None:
        try:
            llm_service = get_llm_service()
            _tutor_service = TutorService(llm_service)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize tutor service: {str(e)}"
            )
    return _tutor_service


def get_visualization_service() -> VisualizationService:
    """Get singleton visualization service instance."""
    global _visualization_service
    if _visualization_service is None:
        _visualization_service = VisualizationService()
    return _visualization_service


def check_environment():
    """Dependency to ensure environment is properly set up."""
    if not setup_environment():
        raise HTTPException(
            status_code=500,
            detail="Environment setup failed. Please check API key configuration.",
        )