# Image Reconstruction (Frontend + Backend)

Upload an image, run a reconstruction model (.pth), view progress with cancel support, and download the output.

- Backend: `backend/` (FastAPI)
- Frontend: `frontend/` (static HTML/JS)

## Quick Start

**Requirements:** Python 3.10+ installed

**Run everything with one command:**

```bash
# Windows
python run_all.py --reload

# macOS/Linux
python3 run_all.py --reload
```

This automatically:
- Creates virtual environment (`.venv`)
- Installs dependencies
- Starts backend server (FastAPI on port 8000)
- Starts frontend server (port 5173)
- Opens the app in your browser

**Optional flags:**
- `--device {cuda|cpu|auto}` - Force device for model
- `--model-path <path/to/model.pth>` - Custom model path
- `--max-upload-mb 20` - Max upload size
- `--backend-port 8000` - Backend port
- `--frontend-port 5173` - Frontend port
- `--no-browser` - Skip auto-open browser

## Configuration

Edit `config.json` to customize settings:

```json
{
  "backend": {
    "port": 8000,
    "model": {
      "path": "backend/data/models/model.pth",
      "device": "auto"
    },
    "upload": {
      "max_size_mb": 10
    }
  },
  "frontend": {
    "port": 5173
  }
}
```

See [CONFIG.md](CONFIG.md) for complete options.

## API Endpoints

- `GET /api/jobs/{job_id}` - Check job progress
- `DELETE /api/jobs/{job_id}` - Cancel job
- `GET /api/jobs/{job_id}/result` - Download result

## Manual Setup (Optional)

<details>
<summary>Click to expand manual setup instructions</summary>

### Backend

**Windows:**
```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate
pip install -r backend\requirements.txt
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
python -m http.server 5173
```

Open `http://localhost:5173`

</details>
