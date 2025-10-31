"""Job queue management for asynchronous image reconstruction tasks.

This module provides the JobManager class that handles the lifecycle of reconstruction
jobs including queueing, execution in background threads, status tracking, progress
reporting, and cancellation.
"""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Dict, Optional, Callable

from .reconstructor import Reconstructor, Cancelled


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
        self.reconstructor = reconstructor
        self.uploads_dir = uploads_dir
        self.outputs_dir = outputs_dir
        self._jobs: Dict[str, Dict] = {}
        self._lock = threading.Lock()

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

    def enqueue(self, job_id: str, input_path: str):
        """Create and enqueue a new reconstruction job.

        Creates a new job entry with initial metadata and starts a background worker
        thread to process it. The worker thread is daemonized and will be automatically
        terminated when the main program exits.

        Args:
            job_id: Unique identifier for this job (typically a UUID).
            input_path: Full path to the uploaded input image file.

        Example:
            >>> manager.enqueue(
            ...     job_id="abc123",
            ...     input_path="/uploads/abc123_photo.png"
            ... )
        """
        with self._lock:
            self._jobs[job_id] = {
                "job_id": job_id,
                "status": "queued",
                "progress": 0,
                "message": "queued",
                "input_path": input_path,
                "output_path": str(Path(self.outputs_dir) / f"{job_id}.png"),
                "cancel": False,
                "error": None,
            }

        # Start background worker thread for this job
        t = threading.Thread(target=self._worker, args=(job_id,), daemon=True)
        t.start()

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
        with self._lock:
            job = self._jobs.get(job_id)
            if not job or job["status"] in ("completed", "failed", "cancelled"):
                return False
            job["cancel"] = True
            job["message"] = "cancelling"
            job["status"] = "cancelling"
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
        def progress(pct: int, msg: str):
            """Progress callback to update job metadata."""
            self._update(job_id, progress=pct, message=msg)

        def cancelled() -> bool:
            """Cancellation check callback."""
            with self._lock:
                return self._jobs[job_id].get("cancel", False)

        self._update(job_id, status="running", message="starting")
        job = self.get(job_id)
        try:
            # Run the reconstruction process
            self.reconstructor.reconstruct(
                job["input_path"],
                job["output_path"],
                progress=progress,
                cancelled=cancelled
            )
            self._update(job_id, status="completed", message="completed")
        except Cancelled:
            self._update(job_id, status="cancelled", message="cancelled by user")
        except Exception as e:
            self._update(job_id, status="failed", message="failed", error=str(e))

