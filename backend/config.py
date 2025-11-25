"""Configuration module for the Image Reconstruction Backend.

This module provides the Config dataclass that manages all application settings,
including directory paths, upload constraints, and CORS configuration.

Configuration is loaded from centralized config.json file and can be overridden
by environment variables.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set

from .config_loader import get_config_loader

# Get logger
logger = logging.getLogger("image_reconstruction.config")


@dataclass
class Config:
    """Application configuration container.

    This dataclass holds all configuration parameters needed for the backend application,
    including directory paths, file upload constraints, and CORS settings.

    Configuration is loaded from centralized config.json and can be overridden by
    environment variables. This ensures single source of truth for all settings.

    Attributes:
        base_dir: Base directory of the backend application (parent of this file).
        data_dir: Root directory for all data storage.
        uploads_dir: Directory where uploaded images are temporarily stored.
        outputs_dir: Directory where reconstructed images are saved.
        models_dir: Directory where ML models are stored.
        model_path: Full path to the PyTorch model file.
        allowed_origins: List of allowed CORS origins for API access.
        max_upload_mb: Maximum allowed upload file size in megabytes.
        allowed_mime: Set of allowed MIME types for uploaded images.
        allowed_ext: Set of allowed file extensions for uploaded images.
        cleanup_enabled: Whether automatic file cleanup is enabled.
        cleanup_interval_hours: Time in hours between cleanup runs.
        cleanup_max_age_hours: Maximum age in hours for files before deletion.

    Example:
        >>> config = Config.from_config()
        >>> print(config.max_upload_bytes)
        10485760
        >>> print(config.uploads_dir)
        Path('/path/to/backend/data/uploads')
    """
    base_dir: Path
    data_dir: Path
    uploads_dir: Path
    outputs_dir: Path
    models_dir: Path
    model_path: Path
    allowed_origins: List[str]
    max_upload_mb: float = 10.0
    allowed_mime: Set[str] = field(default_factory=lambda: {"image/png", "image/jpeg", "image/jpg", "image/webp"})
    allowed_ext: Set[str] = field(default_factory=lambda: {".png", ".jpg", ".jpeg", ".webp"})
    cleanup_enabled: bool = True
    cleanup_interval_hours: float = 1.0
    cleanup_max_age_hours: float = 1.0

    @property
    def max_upload_bytes(self) -> int:
        """Convert max_upload_mb to bytes.

        Returns:
            Maximum upload size in bytes.
        """
        return int(self.max_upload_mb * 1024 * 1024)

    @property
    def default_model_filename(self) -> str:
        """Get the default model filename from the configured model path.

        Returns:
            Model filename (e.g., "ConvNext_REAL-ESRGAN_X4.pth").
        """
        return self.model_path.name

    @property
    def model_dir(self) -> Path:
        """Get the model directory from the configured model path.

        Returns:
            Model directory path (e.g., Path("backend/model")).
        """
        return self.model_path.parent

    @staticmethod
    def from_config() -> "Config":
        """Create Config instance from centralized config.json file.

        This factory method reads configuration from config.json in project root
        and creates necessary directories if they don't exist. Environment variables
        can override any config.json value.

        Configuration Priority:
            1. Environment variables (highest)
            2. config.json values
            3. Code defaults (lowest)

        Environment Variable Overrides:
            - BACKEND_MODEL_PATH: Override model path
            - BACKEND_UPLOAD_MAX_SIZE_MB: Override max upload size
            - BACKEND_CORS_ALLOWED_ORIGINS: Override CORS origins (JSON array)
            - Any other config.json path using uppercase with underscores

        Returns:
            A fully configured Config instance with all directories created.

        Example:
            >>> # Using config.json defaults
            >>> config = Config.from_config()
            >>> config.max_upload_mb
            10.0
            >>>
            >>> # Override with environment variable
            >>> import os
            >>> os.environ["BACKEND_UPLOAD_MAX_SIZE_MB"] = "20"
            >>> config = Config.from_config()
            >>> config.max_upload_mb
            20.0
        """
        logger.info("Loading application configuration from config.json")
        loader = get_config_loader()
        base_dir = Path(__file__).resolve().parent

        # Read directory paths from config
        data_dir_rel = loader.get("backend.directories.data_dir", "backend/data")
        uploads_dir_rel = loader.get("backend.directories.uploads_dir", "backend/data/uploads")
        outputs_dir_rel = loader.get("backend.directories.outputs_dir", "backend/data/outputs")
        models_dir_rel = loader.get("backend.directories.models_dir", "backend/data/models")

        # Convert to absolute paths
        project_root = base_dir.parent
        data_dir = project_root / data_dir_rel
        uploads_dir = project_root / uploads_dir_rel
        outputs_dir = project_root / outputs_dir_rel
        models_dir = project_root / models_dir_rel

        # Create all required directories
        logger.info("Creating required directories")
        for d in (uploads_dir, outputs_dir, models_dir):
            d.mkdir(parents=True, exist_ok=True)
            logger.debug(f"  ✓ {d}")

        # Read model path from config
        model_path_str = loader.get("backend.model.path", "backend/data/models/model.pth")
        model_path = project_root / model_path_str

        # Read CORS origins
        allowed_origins = loader.get("backend.cors.allowed_origins", ["*"])

        # Read upload constraints
        max_upload_mb = float(loader.get("backend.upload.max_size_mb", 10))
        allowed_mime_list = loader.get("backend.upload.allowed_mime_types", [
            "image/png", "image/jpeg", "image/jpg", "image/webp"
        ])
        allowed_ext_list = loader.get("backend.upload.allowed_extensions", [
            ".png", ".jpg", ".jpeg", ".webp"
        ])

        # Read cleanup configuration
        cleanup_enabled = loader.get("backend.cleanup.enabled", True)
        cleanup_interval_hours = float(loader.get("backend.cleanup.interval_hours", 1.0))
        cleanup_max_age_hours = float(loader.get("backend.cleanup.max_age_hours", 1.0))

        logger.info(f"Configuration loaded successfully")
        logger.info(f"  Model path: {model_path}")
        logger.info(f"  Max upload size: {max_upload_mb}MB")
        logger.info(f"  CORS origins: {allowed_origins}")
        logger.info(f"  Allowed extensions: {allowed_ext_list}")
        logger.info(f"  Cleanup enabled: {cleanup_enabled}")
        logger.info(f"  Cleanup interval: {cleanup_interval_hours}h")
        logger.info(f"  Cleanup max age: {cleanup_max_age_hours}h")

        return Config(
            base_dir=base_dir,
            data_dir=data_dir,
            uploads_dir=uploads_dir,
            outputs_dir=outputs_dir,
            models_dir=models_dir,
            model_path=model_path,
            allowed_origins=allowed_origins,
            max_upload_mb=max_upload_mb,
            allowed_mime=set(allowed_mime_list),
            allowed_ext=set(allowed_ext_list),
            cleanup_enabled=cleanup_enabled,
            cleanup_interval_hours=cleanup_interval_hours,
            cleanup_max_age_hours=cleanup_max_age_hours,
        )

    @staticmethod
    def from_env() -> "Config":
        """Create Config instance from config.json (backward compatibility).

        This is an alias for from_config() to maintain backward compatibility
        with existing code that uses Config.from_env().

        Returns:
            A fully configured Config instance.
        """
        return Config.from_config()

