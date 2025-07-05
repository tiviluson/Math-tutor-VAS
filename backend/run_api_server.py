#!/usr/bin/env python3
"""
Startup script for the AI Geometry Tutor API server.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api.main import run_server
from geometry_tutor.llm_utils import setup_environment


def main():
    """Main entry point for the API server."""
    parser = argparse.ArgumentParser(
        description="AI Geometry Tutor API Server"
    )
    parser.add_argument(
        "--host", 
        type=str, 
        default="127.0.0.1", 
        help="Host to bind the server to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to bind the server to (default: 8000)"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Run in debug mode with auto-reload"
    )
    parser.add_argument(
        "--workers", 
        type=int, 
        default=1, 
        help="Number of worker processes (default: 1)"
    )

    args = parser.parse_args()

    # Check environment setup
    print("🔧 Checking environment setup...")
    if not setup_environment():
        print("❌ Environment setup failed!")
        print("Please ensure you have:")
        print("1. Set GOOGLE_API_KEY environment variable")
        print("2. Or created a .env file with GOOGLE_API_KEY=your-key")
        sys.exit(1)

    print("✅ Environment setup complete!")
    print(f"🚀 Starting AI Geometry Tutor API Server...")
    print(f"📡 Server will be available at: http://{args.host}:{args.port}")
    print(f"📚 API Documentation: http://{args.host}:{args.port}/docs")
    print(f"🔍 Health Check: http://{args.host}:{args.port}/health")
    
    if args.debug:
        print("🔧 Running in DEBUG mode with auto-reload")
    
    print("=" * 60)

    try:
        run_server(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
