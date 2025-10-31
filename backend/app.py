from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from .config import Config
from .services.jobs import JobManager
from .services.reconstructor import Reconstructor
from .services.validators import UploadValidator


class BackendApp:
    """OOP wrapper around the FastAPI app and dependencies."""

    def __init__(self, config: Config):
        self.config = config
        self.app = FastAPI(title="Image Reconstruction API")
        self._configure_cors()

        # Core services
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

    def _configure_cors(self) -> None:
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _register_routes(self) -> None:
        app = self.app

        @app.post("/api/jobs")
        async def create_job(file: UploadFile = File(...)):
            job_id = uuid.uuid4().hex
            try:
                upload_path = await self.validator.save(job_id, file)
                self.jobs.enqueue(job_id=job_id, input_path=str(upload_path))
                return {"job_id": job_id}
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/jobs/{job_id}")
        def get_job(job_id: str):
            job = self.jobs.get(job_id)
            if not job:
                raise HTTPException(status_code=404, detail="Job not found")
            return job

        @app.delete("/api/jobs/{job_id}")
        def cancel_job(job_id: str):
            ok = self.jobs.cancel(job_id)
            if not ok:
                raise HTTPException(status_code=404, detail="Job not found or already finished")
            return {"cancelled": True}

        @app.get("/api/jobs/{job_id}/result")
        def get_result(job_id: str):
            meta = self.jobs.get(job_id)
            if not meta:
                raise HTTPException(status_code=404, detail="Job not found")
            if meta.get("status") != "completed":
                return JSONResponse(status_code=409, content={"detail": "Job not completed"})
            out_path = meta.get("output_path")
            if not out_path or not Path(out_path).exists():
                raise HTTPException(status_code=500, detail="Result missing")
            filename = Path(out_path).name
            return FileResponse(out_path, filename=filename, media_type="image/png")

        @app.get("/api/health")
        def health():
            return {
                "status": "ok",
                "model_loaded": self.reconstructor.model_loaded,
                "device": self.reconstructor.device,
            }


def create_app() -> FastAPI:
    cfg = Config.from_env()
    backend = BackendApp(cfg)
    return backend.app


# Uvicorn entrypoint compatibility
app = create_app()
