Backend service for image reconstruction.

Quick start

- Create a Python 3.10+ venv
- Install requirements: `pip install -r requirements.txt`
- Place your model file at `backend/data/models/model.pth` (or set `MODEL_PATH`)
- Run server: `uvicorn app:app --reload --host 0.0.0.0 --port 8000`

Environment variables

- `MODEL_PATH` (optional): Absolute or relative path to *.pth. Defaults to `data/models/model.pth`.
- `ALLOWED_ORIGINS` (optional): Comma-separated list for CORS. Defaults to `*`.
- `DEVICE` (optional): `cuda` or `cpu`. Defaults to `cuda` when available, otherwise `cpu`.
- `MAX_UPLOAD_MB` (optional): Maximum upload size in megabytes. Defaults to `10`.

Endpoints

- `POST /api/jobs` — create a job with uploaded image
- `GET /api/jobs/{job_id}` — get job status and progress
- `DELETE /api/jobs/{job_id}` — cancel a running job
- `GET /api/jobs/{job_id}/result` — download the reconstructed image when done
