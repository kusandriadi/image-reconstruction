# Image Reconstruction (Frontend + Backend)

This repo includes a minimal, separate frontend and backend to upload an image, run a reconstruction model (.pth), show progress with cancel support, and download the output.

- Backend: `backend/` (FastAPI)
- Frontend: `frontend/` (static HTML/JS)

## Navigasi Cepat

- [Quick Start](#quick-start)
  - [Backend (Windows, PowerShell)](#backend-windows-powershell)
  - [Backend (macOS/Linux, bash)](#backend-macoslinux-bash)
  - [Frontend (Static Server)](#frontend-static-server)
- [Single Script (Windows, Linux, macOS)](#single-script-windows-linux-macos)
- [Notes](#notes)

## Quick Start

### Backend (Windows, PowerShell)

1) Create and activate venv
- `py -3.10 -m venv .venv`
- `.\.venv\Scripts\Activate`

2) Install dependencies
- `pip install -r backend\requirements.txt`

3) Place model and set env (optional)
- Put your model at `backend\data\models\model.pth`
- Optionally set env vars:
  - `$env:MODEL_PATH = "backend\data\models\model.pth"`
  - `$env:DEVICE = "cuda"`  (or `"cpu"`)
  - `$env:MAX_UPLOAD_MB = "10"`

4) Run backend server
- `uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000`

### Backend (macOS/Linux, bash)

1) Create and activate venv
- `python3 -m venv .venv`
- `source .venv/bin/activate`

2) Install dependencies
- `pip install -r backend/requirements.txt`

3) Place model and set env (optional)
- Put your model at `backend/data/models/model.pth`
- Optionally set env vars:
  - `export MODEL_PATH=backend/data/models/model.pth`
  - `export DEVICE=cuda`  # or `cpu`
  - `export MAX_UPLOAD_MB=10`

4) Run backend server
- `uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000`

Backend configuration

- `MODEL_PATH`: Path to your `.pth` or `.pt` file.
- `DEVICE`: `cuda` or `cpu`. Defaults to `cuda` if available.
- `MAX_UPLOAD_MB`: Upload limit in MB (default 10).
- `ALLOWED_ORIGINS`: CORS origins (default `*`).

### Frontend (Static Server)

- Windows PowerShell:
  - `cd frontend`
  - `python -m http.server 5173`

- macOS/Linux (bash):
  - `cd frontend`
  - `python3 -m http.server 5173`

- Open `http://localhost:5173`

Optional: point frontend to a different backend origin
- In the browser console: `localStorage.setItem('BACKEND_BASE','http://localhost:8000')`
- Reload the page.

## Notes

- The backend provides progress via polling `GET /api/jobs/{job_id}`.
- Cancel a job with `DELETE /api/jobs/{job_id}`.
- Download the result from `GET /api/jobs/{job_id}/result`.

## Single Script (Windows, Linux, macOS)

- Requirements: Python 3.10+ installed.
- Run from repo root:
  - Windows PowerShell: `py run_all.py --reload` (or `python run_all.py`)
  - macOS/Linux: `python3 run_all.py --reload`
- Optional flags:
  - `--device {cuda|cpu}` (force device)
  - `--model-path <path/to/model.pth>`
  - `--max-upload-mb 20`
  - `--backend-port 8000` / `--frontend-port 5173`
  - `--no-browser` to skip auto-open

What it does
- Creates `.venv` if missing and installs backend requirements.
- Starts backend `uvicorn backend.app:app` and serves `frontend/` via Python’s http.server.
- Opens the frontend in your browser.
