from __future__ import annotations

import threading
from pathlib import Path
from typing import Dict, Optional, Callable

from .reconstructor import Reconstructor, Cancelled


class JobManager:
    def __init__(self, reconstructor: Reconstructor, uploads_dir: str, outputs_dir: str):
        self.reconstructor = reconstructor
        self.uploads_dir = uploads_dir
        self.outputs_dir = outputs_dir
        self._jobs: Dict[str, Dict] = {}
        self._lock = threading.Lock()

    def _update(self, job_id: str, **kwargs):
        with self._lock:
            self._jobs[job_id].update(kwargs)

    def enqueue(self, job_id: str, input_path: str):
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

        t = threading.Thread(target=self._worker, args=(job_id,), daemon=True)
        t.start()

    def cancel(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job or job["status"] in ("completed", "failed", "cancelled"):
                return False
            job["cancel"] = True
            job["message"] = "cancelling"
            job["status"] = "cancelling"
        return True

    def get(self, job_id: str) -> Optional[Dict]:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            return dict(job)

    def _worker(self, job_id: str):
        def progress(pct: int, msg: str):
            self._update(job_id, progress=pct, message=msg)

        def cancelled() -> bool:
            with self._lock:
                return self._jobs[job_id].get("cancel", False)

        self._update(job_id, status="running", message="starting")
        job = self.get(job_id)
        try:
            self.reconstructor.reconstruct(job["input_path"], job["output_path"], progress=progress, cancelled=cancelled)
            self._update(job_id, status="completed", message="completed")
        except Cancelled:
            self._update(job_id, status="cancelled", message="cancelled by user")
        except Exception as e:
            self._update(job_id, status="failed", message="failed", error=str(e))

