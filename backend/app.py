"""FastAPI application module for Image Reconstruction Backend.

This module defines the main FastAPI application with all API endpoints for
image reconstruction jobs, including job creation, status checking, cancellation,
and result retrieval.
"""
from __future__ import annotations

import logging
import uuid
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from .config import Config
from .logger import setup_logger
from .services.jobs import JobManager
from .services.reconstructor import Reconstructor
from .services.validators import UploadValidator

# Get logger
logger = logging.getLogger("image_reconstruction.app")


class BackendApp:
    """Main application wrapper for FastAPI with dependency injection.

    This class encapsulates the FastAPI application instance and manages all core
    services (reconstructor, job manager, validator). It handles CORS configuration
    and route registration using dependency injection pattern.

    Attributes:
        config: Application configuration instance.
        app: FastAPI application instance.
        reconstructor: Image reconstruction service.
        jobs: Job queue and lifecycle manager.
        validator: Upload file validation service.

    Example:
        >>> config = Config.from_env()
        >>> backend = BackendApp(config)
        >>> app = backend.app  # Get FastAPI instance
    """

    def __init__(self, config: Config):
        """Initialize the backend application with all services.

        Args:
            config: Configuration instance containing all application settings.
        """
        logger.info("Initializing BackendApp")
        self.config = config
        self.app = FastAPI(title="Image Reconstruction API")
        self._configure_cors()

        # Core services - dependency injection
        logger.info("Initializing core services")
        self.reconstructor = Reconstructor(model_path=str(self.config.model_path))
        self.jobs = JobManager(
            reconstructor=self.reconstructor,
            uploads_dir=str(self.config.uploads_dir),
            outputs_dir=str(self.config.outputs_dir),
        )
        self.validator = UploadValidator(
            allowed_mime=self.config.allowed_mime,
            allowed_ext=self.config.allowed_ext,
            max_bytes=self.config.max_upload_bytes,
            uploads_dir=self.config.uploads_dir,
        )

        self._register_routes()
        logger.info("BackendApp initialization complete")

    def _configure_cors(self) -> None:
        """Configure CORS middleware for the FastAPI application.

        Sets up Cross-Origin Resource Sharing (CORS) to allow requests from
        configured origins. Allows all methods, headers, and credentials.
        """
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _register_routes(self) -> None:
        """Register all API endpoints with the FastAPI application.

        Defines the following endpoints:
        - POST /api/jobs: Create a new reconstruction job
        - GET /api/jobs/{job_id}: Get job status and progress
        - DELETE /api/jobs/{job_id}: Cancel a running job
        - GET /api/jobs/{job_id}/result: Download reconstructed image
        - GET /api/health: Health check endpoint
        """
        app = self.app

        @app.post("/api/jobs")
        async def create_job(file: UploadFile = File(...)):
            """Create a new image reconstruction job.

            Validates and saves the uploaded image file, then enqueues it for processing.

            Args:
                file: Uploaded image file (multipart/form-data).

            Returns:
                JSON response with job_id: {"job_id": "abc123..."}

            Raises:
                HTTPException 400: Invalid file (empty, corrupted, or unsupported format)
                HTTPException 413: File too large
                HTTPException 415: Unsupported media type
                HTTPException 500: Internal server error during processing
            """
            job_id = uuid.uuid4().hex
            logger.info(f"API: POST /api/jobs - Creating job {job_id}")
            try:
                upload_path = await self.validator.save(job_id, file)
                self.jobs.enqueue(job_id=job_id, input_path=str(upload_path))
                logger.info(f"API: Job {job_id} created successfully")
                return {"job_id": job_id}
            except HTTPException as e:
                logger.warning(f"API: Job {job_id} creation failed: {e.detail}")
                raise
            except Exception as e:
                logger.error(f"API: Job {job_id} creation error: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/jobs/{job_id}")
        def get_job(job_id: str):
            """Get job status and progress information.

            Args:
                job_id: Unique job identifier returned from create_job.

            Returns:
                JSON with job details including status, progress, message, paths, and error.
                Example: {
                    "job_id": "abc123",
                    "status": "running",
                    "progress": 45,
                    "message": "preprocessing",
                    "input_path": "/path/to/input.png",
                    "output_path": "/path/to/output.png",
                    "error": null
                }

            Raises:
                HTTPException 404: Job not found
            """
            logger.debug(f"API: GET /api/jobs/{job_id}")
            job = self.jobs.get(job_id)
            if not job:
                logger.warning(f"API: Job {job_id} not found")
                raise HTTPException(status_code=404, detail="Job not found")
            return job

        @app.delete("/api/jobs/{job_id}")
        def cancel_job(job_id: str):
            """Cancel a running or queued job.

            Jobs that are already completed, failed, or cancelled cannot be cancelled.

            Args:
                job_id: Unique job identifier.

            Returns:
                JSON confirmation: {"cancelled": true}

            Raises:
                HTTPException 404: Job not found or already finished
            """
            logger.info(f"API: DELETE /api/jobs/{job_id} - Cancel requested")
            ok = self.jobs.cancel(job_id)
            if not ok:
                logger.warning(f"API: Cannot cancel job {job_id}")
                raise HTTPException(status_code=404, detail="Job not found or already finished")
            logger.info(f"API: Job {job_id} cancelled")
            return {"cancelled": True}

        @app.get("/api/jobs/{job_id}/result")
        def get_result(job_id: str):
            """Download the reconstructed image result.

            Returns the processed image file. Only available when job status is "completed".

            Args:
                job_id: Unique job identifier.

            Returns:
                FileResponse with the reconstructed PNG image.

            Raises:
                HTTPException 404: Job not found
                HTTPException 409: Job not completed yet (still queued/running)
                HTTPException 500: Result file missing or corrupted
            """
            logger.info(f"API: GET /api/jobs/{job_id}/result")
            meta = self.jobs.get(job_id)
            if not meta:
                logger.warning(f"API: Job {job_id} not found for result download")
                raise HTTPException(status_code=404, detail="Job not found")
            if meta.get("status") != "completed":
                logger.warning(f"API: Job {job_id} not completed (status: {meta.get('status')})")
                return JSONResponse(status_code=409, content={"detail": "Job not completed"})
            out_path = meta.get("output_path")
            if not out_path or not Path(out_path).exists():
                logger.error(f"API: Result file missing for job {job_id}: {out_path}")
                raise HTTPException(status_code=500, detail="Result missing")
            filename = Path(out_path).name
            logger.info(f"API: Serving result for job {job_id}: {filename}")
            return FileResponse(out_path, filename=filename, media_type="image/png")

        @app.get("/api/health")
        def health():
            """Health check endpoint.

            Returns API health status and model information.

            Returns:
                JSON with status, model_loaded flag, and device (cpu/cuda).
                Example: {
                    "status": "ok",
                    "model_loaded": true,
                    "device": "cuda"
                }
            """
            logger.debug("API: GET /api/health")
            return {
                "status": "ok",
                "model_loaded": self.reconstructor.model_loaded,
                "device": self.reconstructor.device,
            }

        @app.get("/api/config")
        def get_config():
            """Get frontend configuration from centralized config.

            Returns configuration parameters needed by the frontend application.
            This ensures frontend and backend share the same configuration source.

            Returns:
                JSON with complete frontend configuration including polling interval,
                UI settings, labels, messages, and other frontend-specific parameters.
            """
            from .config_loader import get_config_loader
            loader = get_config_loader()

            # Default values
            default_labels = {
                "input": "Input Image",
                "output": "Output",
                "ok_button": "OK",
                "cancel_button": "Cancel",
                "download_button": "Download Result"
            }
            default_messages = {
                "uploading": "Uploading...",
                "cancelling": "Cancelling...",
                "file_too_large": "File too large (max {max_size}MB)",
                "file_type_not_allowed": "File type not allowed. Use: {allowed_types}",
                "polling_error": "Polling error: {error}",
                "create_job_failed": "Failed to create job"
            }

            return {
                "backend_url": loader.get("frontend.backend_url", "http://localhost:8000"),
                "file_input": {
                    "accept": loader.get("frontend.file_input.accept", "image/*"),
                },
                "polling": {
                    "interval_ms": loader.get("frontend.polling.interval_ms", 800),
                    "retry_attempts": loader.get("frontend.polling.retry_attempts", 3),
                },
                "ui": {
                    "title": loader.get("frontend.ui.title", "Image Reconstruction"),
                    "labels": loader.get("frontend.ui.labels", default_labels),
                    "messages": loader.get("frontend.ui.messages", default_messages),
                    "preview_enabled": loader.get("frontend.ui.preview_enabled", True),
                    "download_enabled": loader.get("frontend.ui.download_enabled", True),
                    "show_progress_bar": loader.get("frontend.ui.show_progress_bar", True),
                    "preview_alt_text": loader.get("frontend.ui.preview_alt_text", "Output preview"),
                },
                "upload": {
                    "max_size_mb": self.config.max_upload_mb,
                    "allowed_extensions": list(self.config.allowed_ext),
                    "allowed_mime_types": list(self.config.allowed_mime),
                },
            }


def create_app() -> FastAPI:
    """Factory function to create and configure the FastAPI application.

    This function creates a Config instance from environment variables,
    initializes the BackendApp with all services, and returns the FastAPI app instance.

    Returns:
        Configured FastAPI application ready to serve requests.

    Example:
        >>> app = create_app()
        >>> # Use with uvicorn:
        >>> # uvicorn backend.app:app --reload
    """
    # Setup logger first
    setup_logger()

    logger.info("=" * 60)
    logger.info("Image Reconstruction API - Starting")
    logger.info("=" * 60)

    cfg = Config.from_env()
    backend = BackendApp(cfg)

    logger.info("=" * 60)
    logger.info("Image Reconstruction API - Ready")
    logger.info("=" * 60)

    return backend.app


# Uvicorn entrypoint compatibility
# This allows running: uvicorn backend.app:app
app = create_app()
