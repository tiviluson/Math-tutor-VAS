"""
LLM integration and utility functions for the AI Geometry Tutor system.
"""

import os
import json
from typing import Optional, List
from langchain_google_genai import ChatGoogleGenerativeAI


def initialize_llm(
    model_name: str = "gemini-2.0-flash-exp", temperature=0.1, max_output_token=2048
) -> Optional[ChatGoogleGenerativeAI]:
    """Initialize the Google Gemini LLM with appropriate settings."""
    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            max_output_tokens=max_output_token,
        )
        return llm
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        print("Please make sure you have set the GOOGLE_API_KEY environment variable")
        return None


def safe_json_parse(text: str, default: Optional[dict] = None) -> dict:
    """Safely parse JSON from LLM output, handling common formatting issues."""
    if default is None:
        default = {}

    try:
        # Try to find JSON in the text
        start_idx = text.find("{")
        end_idx = text.rfind("}") + 1

        if start_idx != -1 and end_idx != 0:
            json_str = text[start_idx:end_idx]
            return json.loads(json_str)
        else:
            return default
    except json.JSONDecodeError:
        return default


def setup_environment():
    """Setup environment variables and configuration."""
    from dotenv import load_dotenv
    
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Check if Google API key is set
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Warning: GOOGLE_API_KEY environment variable is not set.")
        print("Please set it using: export GOOGLE_API_KEY='your-api-key'")
        print("Or create a .env file with: GOOGLE_API_KEY=your-api-key")
        return False
    
    return True
