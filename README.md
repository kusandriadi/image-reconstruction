# Image Reconstruction App

AI-powered image reconstruction using PyTorch REAL-ESRGAN models with modern web interface.

---

## Quick Start

### 1. Download Model Files

```bash
scripts/download-models.sh
```

Downloads `REAL-ESRGAN.pth` and `ConvNext_REAL-ESRGAN.pth` to `backend/model/`

Manual alternative: [Download from OneDrive](https://binusianorg-my.sharepoint.com/personal/kus_andriadi_binus_ac_id/_layouts/15/guestaccess.aspx?share=EnNjotrV4F1Gp4RR3KVyXggB2y7v8tz3T2cxcbCqtzL5yA&e=UHQUPT)

### 2. Run with Docker

```bash
docker-compose up -d --build
```

- Frontend: http://localhost
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 3. Run Locally (no Docker)

```bash
python run_all.py
```

Sets up a venv, installs deps, starts backend (FastAPI) and frontend (static server), opens browser.

---

## VPS Deployment

```bash
# Deploy with SSL
scripts/deploy.sh example.com admin@example.com

# Update after code changes
scripts/restart.sh

# Stop
scripts/stop.sh

# Status dashboard
scripts/info.sh

# Live logs
scripts/logs.sh
```

---

## Configuration

All settings live in `config.json`. Environment variables override any value using uppercase + underscores (e.g., `backend.model.device` -> `BACKEND_MODEL_DEVICE`).

Key settings:

| Setting | Default | Description |
|---|---|---|
| `backend.model.device` | `"auto"` | `auto`, `cpu`, or `cuda` |
| `backend.upload.max_size_mb` | `10` | Max upload size in MB |
| `backend.jobs.max_concurrent` | `2` | Max parallel processing jobs |
| `backend.cleanup.interval_hours` | `1` | Cleanup interval |
| `backend.cleanup.max_age_hours` | `1` | Max file age before deletion |
| `frontend.polling.interval_ms` | `800` | Job status polling interval |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/reconstructions` | Upload image and create reconstruction job |
| `GET` | `/api/reconstructions/{id}` | Get job status and progress |
| `DELETE` | `/api/reconstructions/{id}` | Cancel a running job |
| `GET` | `/api/reconstructions/{id}/result` | Download reconstructed image |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/config` | Frontend configuration |

---

## Project Structure

```
image-reconstruction/
├── config.json              # All settings (single source of truth)
├── run_all.py               # Local dev runner
├── Dockerfile               # Backend container
├── docker-compose.yml       # Backend + Nginx frontend
├── nginx.conf               # Reverse proxy + security
├── backend/
│   ├── app.py               # FastAPI app + routes
│   ├── config.py            # Config dataclass
│   ├── config_loader.py     # JSON config reader
│   ├── logger.py            # Logging setup
│   ├── model/               # .pth model files
│   ├── models/              # PyTorch model architectures
│   └── services/
│       ├── reconstructor.py # Model loading + inference
│       ├── jobs.py          # Job queue manager
│       ├── cleanup.py       # Background file cleanup
│       └── validators.py    # Upload validation
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
└── scripts/
    ├── deploy.sh            # VPS deployment with SSL
    ├── restart.sh           # Git pull + rebuild
    ├── stop.sh              # Graceful shutdown
    ├── info.sh              # Status dashboard
    ├── logs.sh              # Live log viewer
    └── download-models.sh   # Download model files
```

---

## Tech Stack

- **Backend:** Python 3.10+, FastAPI, PyTorch, Uvicorn
- **Frontend:** HTML, CSS, JavaScript (no framework)
- **Deployment:** Docker, Docker Compose, Nginx
- **Models:** REAL-ESRGAN (4x upscale), ConvNext REAL-ESRGAN (4x upscale)
