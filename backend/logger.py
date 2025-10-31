"""Centralized logging configuration for the application.

This module provides a configured logger instance that uses settings from config.json.
All modules should import and use this logger for consistent logging output.
"""
from __future__ import annotations

import logging
import sys
from typing import Optional

from .config_loader import get_config_loader


def setup_logger(name: str = "image_reconstruction", level: Optional[str] = None) -> logging.Logger:
    """Setup and configure application logger.

    Args:
        name: Logger name (default: "image_reconstruction")
        level: Log level override (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               If None, reads from config.json

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Load config
    loader = get_config_loader()

    # Get log level from config or parameter
    if level is None:
        level = loader.get("logging.level", "INFO")

    # Get format from config
    log_format = loader.get(
        "logging.format",
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Set log level
    logger.setLevel(getattr(logging, level.upper()))

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))

    # Create formatter
    formatter = logging.Formatter(log_format)
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    return logger


# Create default logger instance
logger = setup_logger()


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Logger instance
    """
    return logging.getLogger(f"image_reconstruction.{name}")
