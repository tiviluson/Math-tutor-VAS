"""
Tutoring interaction endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends

from ..models.requests import ValidationRequest, SessionRequest
from ..models.responses import HintResponse, ValidationResponse, SolutionResponse
from ..dependencies import get_session_service

router = APIRouter()


@router.post("/hint", response_model=HintResponse)
async def request_hint(
    request: SessionRequest,
    session_service=Depends(get_session_service)
) -> HintResponse:
    """Request a hint for the current question."""
    tutor = session_service.get_session(request.session_id)
    if not tutor:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    try:
        # Get current state
        status = tutor.get_status()
        if not status["success"]:
            raise HTTPException(status_code=400, detail=status["error"])

        if status["session_complete"]:
            raise HTTPException(status_code=400, detail="Session already complete")

        # Request hint
        hint_result = tutor.request_hint()

        if not hint_result["success"]:
            return HintResponse(
                success=False,
                hint_text=hint_result.get("error", "Failed to generate hint"),
                hint_level=status["hint_level"],
                max_hints_reached=hint_result.get("max_hints_reached", False),
            )

        return HintResponse(
            success=True,
            hint_text=hint_result["hint_text"],
            hint_level=hint_result["hint_level"],
            max_hints_reached=hint_result["max_hints_reached"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate hint: {str(e)}"
        )


@router.post("/validate", response_model=ValidationResponse)
async def validate_solution(
    request: ValidationRequest,
    session_service=Depends(get_session_service)
) -> ValidationResponse:
    """Validate a student's solution for the current question and automatically move to next if correct."""
    if not request.user_input:
        raise HTTPException(status_code=400, detail="Solution text is required")

    tutor = session_service.get_session(request.session_id)
    if not tutor:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    try:
        status = tutor.get_status()
        if not status["success"]:
            raise HTTPException(status_code=400, detail=status["error"])

        if status["session_complete"]:
            raise HTTPException(status_code=400, detail="Session already complete")

        # Validate the solution using the API tutor
        validation_result = tutor.validate_user_solution(request.user_input)

        if not validation_result["success"]:
            raise HTTPException(status_code=400, detail=validation_result["error"])

        # Automatically move to next question if the solution is correct
        moved_to_next = False
        current_question_index = status["current_question_index"]
        session_complete = status["session_complete"]

        if validation_result["is_correct"]:
            try:
                next_result = tutor.move_to_next_question()
                if next_result["success"]:
                    moved_to_next = True
                    current_question_index = next_result["current_question_index"]
                    session_complete = next_result["session_complete"]
            except Exception:
                # If moving to next fails, continue anyway
                pass

        return ValidationResponse(
            success=True,
            is_correct=validation_result["is_correct"],
            feedback=validation_result["feedback"],
            score=validation_result["score"],
            moved_to_next=moved_to_next,
            current_question_index=current_question_index,
            session_complete=session_complete,
            input_type=validation_result.get("input_type", "unknown"),
            message_type=validation_result.get("message_type", "validation"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to validate solution: {str(e)}"
        )


@router.get("/solution", response_model=SolutionResponse)
async def get_solution(
    session_id: str,
    session_service=Depends(get_session_service)
) -> SolutionResponse:
    """Get the complete solution for the current question and automatically move to the next question."""
    tutor = session_service.get_session(session_id)
    if not tutor:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    try:
        status = tutor.get_status()
        if not status["success"]:
            raise HTTPException(status_code=400, detail=status["error"])

        if status["session_complete"]:
            raise HTTPException(status_code=400, detail="Session already complete")

        # Get the complete solution using the API tutor
        solution_result = tutor.get_complete_solution()

        if not solution_result["success"]:
            raise HTTPException(status_code=400, detail=solution_result["error"])

        # Automatically move to next question (bypass validation)
        moved_to_next = False
        current_question_index = status["current_question_index"]
        session_complete = status["session_complete"]

        try:
            next_result = tutor.move_to_next_question()
            if next_result["success"]:
                moved_to_next = True
                current_question_index = next_result["current_question_index"]
                session_complete = next_result["session_complete"]
        except Exception:
            # If moving to next fails, continue anyway
            pass

        return SolutionResponse(
            success=True,
            solution_text=solution_result["solution_text"],
            moved_to_next=moved_to_next,
            current_question_index=current_question_index,
            session_complete=session_complete,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate solution: {str(e)}"
        )