"""
Centralized logging configuration.
"""

import logging
import sys
from typing import Optional

from .config import get_settings


def setup_logging(
    level: Optional[str] = None,
    format_str: Optional[str] = None
) -> logging.Logger:
    """
    Setup centralized logging configuration.
    
    Args:
        level: Log level override
        format_str: Log format override
        
    Returns:
        Configured logger instance
    """
    settings = get_settings()
    
    # Use provided values or fallback to settings
    log_level = level or settings.log_level
    log_format = format_str or settings.log_format
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=True  # Override any existing configuration
    )
    
    # Get application logger
    logger = logging.getLogger("geometry_tutor")
    logger.setLevel(getattr(logging, log_level))
    
    # Suppress noisy third-party loggers in production
    if not settings.debug:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("langchain").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    logger.info(f"Logging configured with level: {log_level}")
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a named logger instance."""
    return logging.getLogger(f"geometry_tutor.{name}")