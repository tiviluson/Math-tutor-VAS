"""
Request logging middleware.
"""

import time
from fastapi import FastAPI


def setup_request_logging(app: FastAPI) -> None:
    """Setup request logging middleware for the FastAPI application."""
    
    @app.middleware("http")
    async def log_requests(request, call_next):
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