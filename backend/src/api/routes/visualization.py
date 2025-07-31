"""
Visualization endpoints for geometric diagram generation.
"""

from fastapi import APIRouter, HTTPException, Depends

from ..models.responses import IllustrationResponse
from ..dependencies import get_session_service, get_visualization_service

router = APIRouter()


@router.get("/illustration", response_model=IllustrationResponse)
async def get_illustration(
    session_id: str,
    session_service=Depends(get_session_service),
    viz_service=Depends(get_visualization_service)
) -> IllustrationResponse:
    """Get a geometric illustration/visualization for the current problem."""
    tutor = session_service.get_session(session_id)
    if not tutor:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    try:
        # Get session status to retrieve problem and illustration steps
        status = tutor.get_enhanced_status()
        if not status["success"]:
            raise HTTPException(status_code=400, detail=status["error"])

        # Extract required data for visualization
        original_problem = status.get("original_problem", "")
        illustration_steps = status.get("illustration_steps", [])

        # Generate visualization using service
        result = viz_service.generate_illustration(
            session_id=session_id,
            problem=original_problem,
            illustration_steps=illustration_steps
        )

        return IllustrationResponse(
            success=result["success"],
            message=result["message"],
            b64_string_viz=result.get("b64_string_viz"),
            error=result.get("error")
        )

    except HTTPException:
        raise
    except Exception as e:
        return IllustrationResponse(
            success=False,
            message="Failed to generate illustration",
            b64_string_viz=None,
            error=str(e),
        )