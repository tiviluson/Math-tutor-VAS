"""
Error handling middleware and exception handlers.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse


def setup_error_handlers(app: FastAPI) -> None:
    """Setup error handlers for the FastAPI application."""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code, 
            content={"error": exc.detail, "success": False}
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(exc)}", "success": False},
        )