"""Centralized configuration loader for the application.

This module provides utilities to load configuration from a central config.json file,
with support for environment variable overrides. This ensures single source of truth
for all configuration parameters across backend and frontend.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict


class ConfigLoader:
    """Loader for centralized application configuration.

    Reads configuration from config.json in the project root and allows
    environment variables to override specific values. This provides a
    single source of truth for configuration while maintaining flexibility.

    Environment Variable Override Priority:
    1. Environment variables (highest priority)
    2. config.json values
    3. Default values in code (lowest priority)

    Example:
        >>> loader = ConfigLoader()
        >>> max_upload = loader.get("backend.upload.max_size_mb")
        >>> device = loader.get("backend.model.device", default="cpu")
    """

    def __init__(self, config_path: str | Path | None = None):
        """Initialize the config loader.

        Args:
            config_path: Path to config.json file. If None, searches in parent
                        directory of backend folder.
        """
        if config_path is None:
            # Default: config.json in project root (parent of backend/)
            backend_dir = Path(__file__).resolve().parent
            config_path = backend_dir.parent / "config.json"

        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load()

    def _load(self):
        """Load configuration from JSON file.

        Raises:
            FileNotFoundError: If config file doesn't exist.
            json.JSONDecodeError: If config file is not valid JSON.
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config = json.load(f)

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation.

        Supports nested keys using dot notation (e.g., "backend.upload.max_size_mb").
        Environment variables can override config values using uppercase and
        underscores (e.g., BACKEND_UPLOAD_MAX_SIZE_MB).

        Args:
            key_path: Dot-separated path to config value (e.g., "backend.port").
            default: Default value if key not found.

        Returns:
            Configuration value, environment variable override, or default.

        Example:
            >>> loader = ConfigLoader()
            >>> loader.get("backend.port")  # Returns 8000 from config.json
            >>> os.environ["BACKEND_PORT"] = "9000"
            >>> loader.get("backend.port")  # Returns 9000 from env var
        """
        # Check environment variable override first
        env_key = key_path.upper().replace(".", "_")
        env_value = os.getenv(env_key)
        if env_value is not None:
            # Try to parse as JSON for lists/dicts, otherwise return as string
            try:
                return json.loads(env_value)
            except (json.JSONDecodeError, ValueError):
                return env_value

        # Navigate through nested dictionary
        keys = key_path.split(".")
        value = self._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_all(self) -> Dict[str, Any]:
        """Get the entire configuration dictionary.

        Returns:
            Complete configuration as a dictionary.
        """
        return self._config.copy()

    def reload(self):
        """Reload configuration from file.

        Useful if config.json has been modified and needs to be reloaded
        without restarting the application.
        """
        self._load()


# Singleton instance for easy import
_loader: ConfigLoader | None = None


def get_config_loader() -> ConfigLoader:
    """Get singleton ConfigLoader instance.

    Returns:
        Shared ConfigLoader instance.

    Example:
        >>> from backend.config_loader import get_config_loader
        >>> loader = get_config_loader()
        >>> port = loader.get("backend.port")
    """
    global _loader
    if _loader is None:
        _loader = ConfigLoader()
    return _loader
