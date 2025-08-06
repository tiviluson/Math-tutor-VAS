"""
Session management endpoints.
"""

from typing import Dict, Any, Union
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends

from ..models.requests import ProblemRequest
from ..models.responses import SessionStatus
from ..dependencies import get_session_service, get_tutor_service

router = APIRouter()


@router.post(
    "/sessions",
    response_model=Dict[str, Union[str, int]],
)
async def create_session(
    request: ProblemRequest, 
    background_tasks: BackgroundTasks,
    session_service=Depends(get_session_service),
    tutor_service=Depends(get_tutor_service)
) -> Dict[str, Union[str, int]]:
    """
    Create a new tutoring session with a geometry problem.

    - If is_img=true: Processes the base64 image to extract problem text
    - If is_img=false: Uses the provided problem_text directly

    Only one of problem_text or img should be provided based on the is_img flag.

    Returns session_id for subsequent API calls.
    """
    try:
        # Process the problem text based on is_img flag
        if request.is_img and request.img is not None:
            # Process image to extract problem text
            try:
                final_problem_text = await tutor_service.process_image_to_text(request.img)
            except Exception as img_error:
                raise HTTPException(
                    status_code=400, detail=f"Failed to process image: {str(img_error)}"
                )
        else:
            # Use provided problem text
            final_problem_text = request.problem_text

        # Validate that we have some problem text
        if not final_problem_text.strip():
            raise HTTPException(
                status_code=400,
                detail=(
                    "Failed to extract problem text from image"
                    if request.img
                    else "Problem text is required"
                ),
            )

        # Create session through service
        result = session_service.create_session(final_problem_text)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        # Schedule cleanup task
        background_tasks.add_task(session_service.cleanup_expired_sessions)

        return {
            "session_id": result["session_id"],
            "message": "Session created successfully",
            "total_questions": result.get("total_questions", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create session: {str(e)}"
        )


@router.get("/status", response_model=SessionStatus)
async def get_session_status(
    session_id: str,
    session_service=Depends(get_session_service)
) -> SessionStatus:
    """Get current status of a tutoring session."""
    tutor = session_service.get_session(session_id)
    if not tutor:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    try:
        status = tutor.get_enhanced_status()
        session_info = session_service.get_session_info(session_id)

        if not status["success"]:
            raise HTTPException(status_code=400, detail=status["error"])

        if not session_info:
            raise HTTPException(status_code=404, detail="Session info not found")

        return SessionStatus(
            session_id=session_id,
            success=status["success"],
            current_question_index=status["current_question_index"] + 1,
            total_questions=status["total_questions"],
            current_question=status["current_question"],
            hint_level=status["hint_level"],
            hints_used=status["hints_used"],
            is_validated=status["is_validated"],
            session_complete=status["session_complete"],
            known_facts=status["known_facts"],
            original_problem=status["original_problem"],
            previously_solved_questions=status["previously_solved_questions"],
            current_question_solution=status["current_question_solution"],
            illustration_steps=status["illustration_steps"],
            created_at=session_info["created_at"],
            last_activity=session_info["last_activity"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get session status: {str(e)}"
        )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    session_service=Depends(get_session_service)
):
    """Delete a tutoring session."""
    result = session_service.delete_session(session_id)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    return {"success": True, "message": "Session deleted successfully"}


@router.get("/sessions")
async def list_active_sessions(
    session_service=Depends(get_session_service)
) -> Dict[str, Any]:
    """List all active sessions (for debugging/monitoring)."""
    return session_service.list_active_sessions()