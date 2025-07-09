"""
FastAPI-based REST API server for the AI Geometry Tutor.
Supports both text-based geometry problems and image uploads for problem extraction.
"""

import uuid
import time
import base64
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Import the geometry tutor
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from geometry_tutor.llm_utils import setup_environment
from .tutor import ApiGeometryTutor


# Pydantic models for API requests and responses
class ProblemRequest(BaseModel):
    problem_text: str = Field(
        default="", description="Vietnamese geometry problem text (required if is_img=false)"
    )
    is_img: bool = Field(
        default=False, description="Whether the request includes an image instead of text"
    )
    img: Optional[str] = Field(
        default=None, description="Base64 encoded image of the geometry problem (required if is_img=true)"
    )


class SolutionRequest(BaseModel):
    session_id: str = Field(..., description="Session ID from problem creation")
    # action: str = Field(
    #     ..., description="Action to perform: hint, submit, solution, next"
    # )
    solution_text: Optional[str] = Field(
        None, description="Solution text for submit action"
    )


class SessionRequest(BaseModel):
    session_id: str = Field(..., description="Session ID from problem creation")


class SessionStatus(BaseModel):
    session_id: str
    success: bool
    current_question_index: int
    total_questions: int
    current_question: str
    hint_level: int
    hints_used: int
    is_validated: bool
    session_complete: bool
    known_facts: List[str]
    original_problem: str
    previously_solved_questions: List[Dict[str, Any]]
    current_question_solution: Optional[str] = None
    illustration_steps: List[str]
    created_at: datetime
    last_activity: datetime


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class HintResponse(BaseModel):
    success: bool
    hint_text: str
    hint_level: int
    max_hints_reached: bool


class ValidationResponse(BaseModel):
    success: bool
    is_correct: bool
    feedback: str
    score: int
    moved_to_next: bool = False
    current_question_index: Optional[int] = None
    session_complete: bool = False


class SolutionResponse(BaseModel):
    success: bool
    solution_text: str
    moved_to_next: bool = False
    current_question_index: Optional[int] = None
    session_complete: bool = False


# Helper function to process image and extract problem text
async def process_image_to_text(image_b64: str) -> str:
    """
    Process base64 encoded image to extract geometry problem text using LLM.
    
    Args:
        image_b64: Base64 encoded image (can include data URL prefix or just base64)
        
    Returns:
        Extracted problem text from image
    """
    try:
        # Validate base64 input
        if not image_b64 or not isinstance(image_b64, str):
            raise ValueError("Invalid base64 image data")
        
        # Clean up base64 string - remove data URL prefix if present
        if image_b64.startswith('data:image/'):
            # Extract just the base64 part after the comma
            if ',' in image_b64:
                image_b64 = image_b64.split(',', 1)[1]
        
        # Basic validation - try to decode base64
        try:
            image_data = base64.b64decode(image_b64)
            if len(image_data) == 0:
                raise ValueError("Empty image data")
        except Exception as decode_error:
            raise ValueError(f"Invalid base64 image: {decode_error}")
        
        # Initialize LLM for vision processing
        from geometry_tutor.llm_utils import initialize_llm
        llm = initialize_llm()
        
        if not llm:
            raise ValueError("Failed to initialize LLM for image processing")
        
        # Create the vision prompt
        prompt = """Bạn là một chuyên gia toán học, hãy phân tích hình ảnh bài toán hình học này và trích xuất thông tin.

Hãy thực hiện các nhiệm vụ sau:
1. Trích xuất toàn bộ văn bản của bài toán (nếu có) trong hình ảnh
2. Mô tả chi tiết hình vẽ/minh họa trong bài toán (nếu có)
3. Xác định xem có hình vẽ/minh họa trong ảnh hay không

Trả về kết quả theo định dạng JSON:
{
    "problem_text": "Văn bản bài toán đầy đủ đã được trích xuất từ hình ảnh",
    "illustration_description": "Mô tả chi tiết hình vẽ nếu có, ngược lại trả về chuỗi rỗng",
    "has_text_in_image": true/false,
    "has_illustration_in_image": true/false
}

Yêu cầu:
- Trích xuất chính xác toàn bộ văn bản trong hình ảnh
- Mô tả chi tiết các yếu tố hình học (điểm, đường, góc, hình dạng, v.v...) nếu có hình vẽ
- Đảm bảo văn bản tiếng Việt chính xác
- Nếu không có văn bản trong hình ảnh, trả về chuỗi rỗng cho problem_text
- Nếu không có hình vẽ minh họa, trả về chuỗi rỗng cho illustration_description và has_illustration_in_image = false
- Đặt has_illustration_in_image = true nếu có bất kỳ hình vẽ, sơ đồ, biểu đồ hình học nào trong ảnh"""

        # Prepare the message with image
        from langchain_core.messages import HumanMessage
        
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
                }
            ]
        )
        
        # Make the LLM call
        try:
            response = llm.invoke([message])
            response_text = response.content
            
            # Ensure response_text is a string
            if isinstance(response_text, list):
                response_text = str(response_text)
            elif not isinstance(response_text, str):
                response_text = str(response_text)
            
            # Try to parse JSON response
            from geometry_tutor.llm_utils import safe_json_parse
            result = safe_json_parse(response_text)
            
            if result and "problem_text" in result:
                # Use the extracted text from LLM
                final_text = result["problem_text"]

                # Add illustration description only if there's actually an illustration in the image
                if result.get("has_illustration_in_image", False) and result.get(
                    "illustration_description"
                ):
                    final_text += (
                        f"\n\n[Mô tả hình vẽ: {result['illustration_description']}]"
                    )

                if final_text.strip():
                    return final_text
                else:
                    return "Không thể trích xuất thông tin từ hình ảnh. Vui lòng cung cấp văn bản bài toán."
            
            # If JSON parsing fails, try to extract text directly from response
            elif response_text.strip():
                return response_text
            
            # If LLM response is empty
            else:
                return "Không thể trích xuất thông tin từ hình ảnh. Vui lòng cung cấp văn bản bài toán."
                    
        except Exception as llm_error:
            print(f"LLM processing failed: {llm_error}")
            raise ValueError(f"Failed to process image with LLM: {llm_error}")
        
    except Exception as e:
        raise ValueError(f"Failed to process image: {str(e)}")


# In-memory session storage (in production, use Redis or database)
class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(hours=2)  # 2 hour timeout

    def create_session(self, tutor: ApiGeometryTutor) -> str:
        """Create a new session and return session ID."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "tutor": tutor,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "active": True,
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[ApiGeometryTutor]:
        """Get session by ID, return None if not found or expired."""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]

        # Check if session is expired
        if datetime.now() - session["last_activity"] > self.session_timeout:
            self.cleanup_session(session_id)
            return None

        # Update last activity
        session["last_activity"] = datetime.now()
        return session["tutor"]

    def cleanup_session(self, session_id: str):
        """Remove session from memory."""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def cleanup_expired_sessions(self):
        """Clean up all expired sessions."""
        expired_sessions = []
        current_time = datetime.now()

        for session_id, session in self.sessions.items():
            if current_time - session["last_activity"] > self.session_timeout:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            self.cleanup_session(session_id)

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session metadata."""
        if session_id not in self.sessions:
            return None
        return {
            "created_at": self.sessions[session_id]["created_at"],
            "last_activity": self.sessions[session_id]["last_activity"],
            "active": self.sessions[session_id]["active"],
        }


# Global session manager
session_manager = SessionManager()

# FastAPI app
app = FastAPI(
    title="AI Geometry Tutor API",
    description="REST API for the AI Geometry Tutor system for Vietnamese high school students",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to check environment setup
def check_environment():
    """Dependency to ensure environment is properly set up."""
    if not setup_environment():
        raise HTTPException(
            status_code=500,
            detail="Environment setup failed. Please check API key configuration.",
        )


# Background task for cleaning up expired sessions
def cleanup_expired_sessions_task():
    """Background task to clean up expired sessions."""
    session_manager.cleanup_expired_sessions()


# API Routes


# @app.get("/", response_model=Dict[str, str])
# async def root():
#     """Root endpoint with API information."""
#     return {
#         "message": "AI Geometry Tutor API",
#         "version": "1.0.0",
#         "docs": "/docs",
#         "status": "running",
#     }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Quick environment check
        setup_environment()
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post(
    "/sessions",
    response_model=Dict[str, Union[str, int]],
    dependencies=[Depends(check_environment)],
)
async def create_session(
    request: ProblemRequest, background_tasks: BackgroundTasks
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
                final_problem_text = await process_image_to_text(request.img)
            except Exception as img_error:
                print(f"Image processing failed: {img_error}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to process image: {str(img_error)}"
                )
        else:
            # Use provided problem text
            final_problem_text = request.problem_text

        # Validate that we have some problem text
        if not final_problem_text.strip():
            raise HTTPException(
                status_code=400, 
                detail="Failed to extract problem text from image" if request.img else "Problem text is required" 
            )

        # Create tutor instance
        tutor = ApiGeometryTutor()

        # Create session
        session_id = session_manager.create_session(tutor)

        # Start the problem (this will parse and set up the session)
        result = tutor.start_problem(final_problem_text)

        if not result["success"]:
            session_manager.cleanup_session(session_id)
            raise HTTPException(status_code=400, detail=result["error"])

        # Schedule cleanup task
        background_tasks.add_task(cleanup_expired_sessions_task)

        return {
            "session_id": session_id,
            "message": "Session created successfully",
            "total_questions": result.get("total_questions", 0),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create session: {str(e)}"
        )


@app.get("/status", response_model=SessionStatus)
async def get_session_status(request: SessionRequest) -> SessionStatus:
    """Get current status of a tutoring session."""
    tutor = session_manager.get_session(request.session_id)
    if not tutor:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    try:
        status = tutor.get_enhanced_status()
        session_info = session_manager.get_session_info(request.session_id)

        if not status["success"]:
            raise HTTPException(status_code=400, detail=status["error"])

        if not session_info:
            raise HTTPException(status_code=404, detail="Session info not found")

        return SessionStatus(
            session_id=request.session_id,
            success=status["success"],
            current_question_index=status["current_question_index"]
            + 1,  # Convert to 1-based for API
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

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get session status: {str(e)}"
        )


@app.post("/hint", response_model=HintResponse)
async def request_hint(request: SessionRequest) -> HintResponse:
    """Request a hint for the current question."""
    tutor = session_manager.get_session(request.session_id)
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

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate hint: {str(e)}"
        )


@app.post("/validate", response_model=ValidationResponse)
async def validate_solution(request: SolutionRequest) -> ValidationResponse:
    """Validate a student's solution for the current question and automatically move to next if correct."""
    if not request.solution_text:
        raise HTTPException(status_code=400, detail="Solution text is required")

    tutor = session_manager.get_session(request.session_id)
    if not tutor:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    try:
        status = tutor.get_status()
        if not status["success"]:
            raise HTTPException(status_code=400, detail=status["error"])

        if status["session_complete"]:
            raise HTTPException(status_code=400, detail="Session already complete")

        # Validate the solution using the API tutor
        validation_result = tutor.validate_user_solution(request.solution_text)

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
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to validate solution: {str(e)}"
        )


@app.get("/solution", response_model=SolutionResponse)
async def get_solution(request: SessionRequest) -> SolutionResponse:
    """Get the complete solution for the current question and automatically move to the next question."""
    tutor = session_manager.get_session(request.session_id)
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

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate solution: {str(e)}"
        )


# @app.post("/sessions/{session_id}/next", response_model=ApiResponse)
# async def next_question(session_id: str) -> ApiResponse:
#     """Move to the next question in the session."""
#     tutor = session_manager.get_session(session_id)
#     if not tutor:
#         raise HTTPException(status_code=404, detail="Session not found or expired")
#
#     try:
#         status = tutor.get_status()
#         if not status["success"]:
#             raise HTTPException(status_code=400, detail=status["error"])
#
#         if status["session_complete"]:
#             return ApiResponse(
#                 success=True,
#                 message="Session already complete",
#                 data={"session_complete": True},
#             )
#
#         # Move to next question using the API tutor
#         next_result = tutor.move_to_next_question()
#
#         if not next_result["success"]:
#             raise HTTPException(status_code=400, detail=next_result["error"])
#
#         return ApiResponse(
#             success=True,
#             message=next_result["message"],
#             data={
#                 "current_question_index": next_result["current_question_index"],
#                 "session_complete": next_result["session_complete"],
#             },
#         )
#
#     except Exception as e:
#         raise HTTPException(
#             status_code=500, detail=f"Failed to move to next question: {str(e)}"
#         )


@app.delete("/sessions", response_model=ApiResponse)
async def delete_session(request: SessionRequest) -> ApiResponse:
    """Delete a tutoring session."""
    if request.session_id not in session_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session_manager.cleanup_session(request.session_id)

    return ApiResponse(success=True, message="Session deleted successfully")


@app.get("/sessions", response_model=Dict[str, Any])
async def list_active_sessions() -> Dict[str, Any]:
    """List all active sessions (for debugging/monitoring)."""
    active_sessions = []

    for session_id, session_data in session_manager.sessions.items():
        active_sessions.append(
            {
                "session_id": session_id,
                "created_at": session_data["created_at"].isoformat(),
                "last_activity": session_data["last_activity"].isoformat(),
                "active": session_data["active"],
            }
        )

    return {"active_sessions": len(active_sessions), "sessions": active_sessions}


@app.get("/test")
async def test_endpoint():
    """Simple test endpoint for debugging"""
    return {"message": "Test endpoint working", "timestamp": time.time()}


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code, content={"error": exc.detail, "success": False}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": f"Internal server error: {str(exc)}", "success": False},
    )


# Request logging middleware for debugging
@app.middleware("http")
async def log_requests(request, call_next):
    import time
    start_time = time.time()
    print(f"🔍 Incoming request: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        print(f"✅ Response: {response.status_code} (took {process_time:.2f}s)")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        print(f"❌ Request failed: {str(e)} (took {process_time:.2f}s)")
        import traceback
        traceback.print_exc()
        raise


# Server configuration
def create_app() -> FastAPI:
    """Factory function to create the FastAPI app."""
    return app


def run_server(host: str = "127.0.0.1", port: int = 8000, debug: bool = False):
    """Run the API server."""
    uvicorn.run(
        "api.main:app" if not debug else "api.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info",
    )


if __name__ == "__main__":
    run_server(debug=True)
