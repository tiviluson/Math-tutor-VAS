"""
FastAPI-based REST API server for the AI Geometry Tutor.
Streamlined main application file with modular route organization.
"""

import uvicorn
from fastapi import FastAPI

# Import route modules
from .routes import health, sessions, tutoring, visualization

# Import middleware setup functions
from .middleware import setup_cors, setup_error_handlers, setup_request_logging

# Import dependencies
from .dependencies import check_environment


def create_app() -> FastAPI:
    """Factory function to create the FastAPI app."""
    # Create FastAPI application
    app = FastAPI(
        title="AI Geometry Tutor API",
        description="REST API for the AI Geometry Tutor system for Vietnamese high school students",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Setup middleware
    setup_cors(app)
    setup_error_handlers(app)
    setup_request_logging(app)

    # Include route modules
    app.include_router(health.router, tags=["health"])
    app.include_router(sessions.router, tags=["sessions"]) 
    app.include_router(tutoring.router, tags=["tutoring"])
    app.include_router(visualization.router, tags=["visualization"])

    return app


# Create app instance
app = create_app()


def run_server(host: str = "127.0.0.1", port: int = 8000, debug: bool = False):
    """Run the API server."""
    uvicorn.run(
        "src.api.main:app" if not debug else "src.api.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info",
    )


if __name__ == "__main__":
    run_server(debug=True)