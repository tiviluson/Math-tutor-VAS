"""
Health check endpoints for API monitoring.
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException

from src.geometry_tutor.llm_utils import setup_environment

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Quick environment check
        setup_environment()
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@router.get("/test")
async def test_endpoint():
    """Simple test endpoint for debugging"""
    import time
    return {"message": "Test endpoint working", "timestamp": time.time()}