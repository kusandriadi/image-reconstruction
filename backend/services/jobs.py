"""Job queue management for asynchronous image reconstruction tasks.

This module provides the JobManager class that handles the lifecycle of reconstruction
jobs including queueing, execution in background threads, status tracking, progress
reporting, and cancellation.
"""
from __future__ import annotations

import logging
import threading
import time
from pathlib import Path
from typing import Dict, Optional, Callable

from .reconstructor import Reconstructor, Cancelled

# Get logger
logger = logging.getLogger("image_reconstruction.jobs")


class JobManager:
    """Asynchronous job queue manager for image reconstruction tasks.

    This class manages the complete lifecycle of reconstruction jobs using background
    worker threads. It provides thread-safe operations for job creation, status tracking,
    progress updates, and cancellation. Each job runs in its own daemon thread.

    Job States:
        - queued: Job is waiting to start
        - running: Job is currently processing
        - completed: Job finished successfully
        - failed: Job encountered an error
        - cancelled: Job was cancelled by user
        - cancelling: Job is in the process of being cancelled

    Attributes:
        reconstructor: The Reconstructor instance used for processing.
        uploads_dir: Directory containing uploaded input images.
        outputs_dir: Directory where reconstructed images are saved.

    Thread Safety:
        All public methods are thread-safe and can be called concurrently from
        multiple threads. Internal state is protected by a threading.Lock.

    Example:
        >>> reconstructor = Reconstructor(model_path="model.pth")
        >>> manager = JobManager(reconstructor, "uploads/", "outputs/")
        >>> manager.enqueue(job_id="abc123", input_path="uploads/abc123_image.png")
        >>> status = manager.get("abc123")
        >>> print(status["progress"])  # 0-100
        >>> manager.cancel("abc123")
    """

    def __init__(self, reconstructor: Reconstructor, uploads_dir: str, outputs_dir: str):
        """Initialize the job manager.

        Args:
            reconstructor: Reconstructor instance for processing images.
            uploads_dir: Directory path containing uploaded input files.
            outputs_dir: Directory path where results will be saved.
        """
        logger.info("Initializing JobManager")
        self.reconstructor = reconstructor
        self.uploads_dir = uploads_dir
        self.outputs_dir = outputs_dir
        self._jobs: Dict[str, Dict] = {}
        self._lock = threading.Lock()
        logger.info(f"JobManager initialized. Uploads: {uploads_dir}, Outputs: {outputs_dir}")

    def _update(self, job_id: str, **kwargs):
        """Thread-safe update of job metadata.

        Args:
            job_id: Unique job identifier.
            **kwargs: Job fields to update (status, progress, message, error, etc.).

        Note:
            This is an internal method and should not be called directly.
        """
        with self._lock:
            self._jobs[job_id].update(kwargs)

    def enqueue(self, job_id: str, input_path: str, model_filename: str = "ConvNext_REAL-ESRGAN.pth"):
        """Create and enqueue a new reconstruction job.

        Creates a new job entry with initial metadata and starts a background worker
        thread to process it. The worker thread is daemonized and will be automatically
        terminated when the main program exits.

        Args:
            job_id: Unique identifier for this job (typically a UUID).
            input_path: Full path to the uploaded input image file.
            model_filename: Filename of the model to use (default: ConvNext_REAL-ESRGAN.pth).

        Example:
            >>> manager.enqueue(
            ...     job_id="abc123",
            ...     input_path="/uploads/abc123_photo.png",
            ...     model_filename="REAL-ESRGAN.pth"
            ... )
        """
        logger.info(f"Enqueueing job {job_id}: {input_path} with model {model_filename}")
        with self._lock:
            self._jobs[job_id] = {
                "job_id": job_id,
                "status": "queued",
                "progress": 0,
                "message": "queued",
                "input_path": input_path,
                "output_path": str(Path(self.outputs_dir) / f"{job_id}.png"),
                "model_filename": model_filename,
                "cancel": False,
                "error": None,
                "start_time": None,
                "elapsed_seconds": None,
            }

        # Start background worker thread for this job
        t = threading.Thread(target=self._worker, args=(job_id,), daemon=True)
        t.start()
        logger.debug(f"Worker thread started for job {job_id}")

    def cancel(self, job_id: str) -> bool:
        """Request cancellation of a running or queued job.

        Sets the cancellation flag for the job. The worker thread will check this
        flag periodically and stop processing. Jobs that are already completed,
        failed, or cancelled cannot be cancelled.

        Args:
            job_id: Unique job identifier.

        Returns:
            True if cancellation was requested successfully, False if job not found
            or already finished.

        Example:
            >>> if manager.cancel("abc123"):
            ...     print("Cancellation requested")
            ... else:
            ...     print("Job not found or already finished")
        """
        logger.info(f"Cancel requested for job {job_id}")
        with self._lock:
            job = self._jobs.get(job_id)
            if not job or job["status"] in ("completed", "failed", "cancelled"):
                logger.warning(f"Cannot cancel job {job_id}: not found or already finished")
                return False
            job["cancel"] = True
            job["message"] = "cancelling"
            job["status"] = "cancelling"
            logger.info(f"Job {job_id} marked for cancellation")
        return True

    def get(self, job_id: str) -> Optional[Dict]:
        """Retrieve current job status and metadata.

        Returns a snapshot of the job's current state including status, progress,
        message, file paths, and any error information.

        Args:
            job_id: Unique job identifier.

        Returns:
            Dictionary containing job metadata, or None if job not found.
            Keys include: job_id, status, progress, message, input_path,
            output_path, cancel, error.

        Example:
            >>> job = manager.get("abc123")
            >>> if job:
            ...     print(f"Status: {job['status']}")
            ...     print(f"Progress: {job['progress']}%")
            ...     print(f"Message: {job['message']}")
        """
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            return dict(job)

    def _worker(self, job_id: str):
        """Background worker thread that processes a single job.

        This method runs in a separate daemon thread for each job. It calls the
        reconstructor with progress and cancellation callbacks, and updates job
        status accordingly.

        Args:
            job_id: Unique job identifier to process.

        Note:
            This is an internal method called by enqueue() and should not be
            called directly.
        """
        logger.info(f"Worker starting for job {job_id}")

        def progress(pct: int, msg: str):
            """Progress callback to update job metadata."""
            self._update(job_id, progress=pct, message=msg)
            logger.debug(f"Job {job_id}: {pct}% - {msg}")

        def cancelled() -> bool:
            """Cancellation check callback."""
            with self._lock:
                return self._jobs[job_id].get("cancel", False)

        # Record start time
        start_time = time.time()
        self._update(job_id, status="running", message="starting", start_time=start_time)
        job = self.get(job_id)
        try:
            model_filename = job.get("model_filename", "ConvNext_REAL-ESRGAN.pth")
            logger.warning(f"Job {job_id}: Using model '{model_filename}'")
            # Construct model path from filename
            model_path = Path("backend/model") / model_filename
            logger.warning(f"Model path: {model_path}")
            # Run the reconstruction process
            self.reconstructor.reconstruct(
                job["input_path"],
                job["output_path"],
                progress=progress,
                cancelled=cancelled,
                model_path=str(model_path)
            )
            # Calculate elapsed time
            elapsed = time.time() - start_time
            self._update(job_id, status="completed", message="completed", elapsed_seconds=round(elapsed, 2))
            logger.info(f"Job {job_id}: Completed successfully in {elapsed:.2f} seconds")
        except Cancelled:
            elapsed = time.time() - start_time
            self._update(job_id, status="cancelled", message="cancelled by user", elapsed_seconds=round(elapsed, 2))
            logger.info(f"Job {job_id}: Cancelled by user after {elapsed:.2f} seconds")
        except Exception as e:
            elapsed = time.time() - start_time
            self._update(job_id, status="failed", message="failed", error=str(e), elapsed_seconds=round(elapsed, 2))
            logger.error(f"Job {job_id}: Failed after {elapsed:.2f} seconds with error: {e}", exc_info=True)

