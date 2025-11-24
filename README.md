# Image Reconstruction App

AI-powered image reconstruction using PyTorch REAL-ESRGAN models with modern web interface.

![BINUS Style UI](https://img.shields.io/badge/UI-BINUS%20Orange-f3931b)
![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)

---

## ✨ Features

- 🎨 BINUS-themed UI with drag & drop
- 🤖 Dual models (ConvNext REAL-ESRGAN / REAL-ESRGAN)
- 📊 Real-time progress tracking
- 🐳 One-command Docker deployment
- ⚡ Fast async API with FastAPI

---

## 🚀 Quick Start

### 1. Download Model Files

```bash
scripts/download-models.sh
```

Downloads `REAL-ESRGAN.pth` and `ConvNext_REAL-ESRGAN.pth` to `backend/model/`

**Manual alternative:** [Download from OneDrive](https://binusianorg-my.sharepoint.com/personal/kus_andriadi_binus_ac_id/_layouts/15/guestaccess.aspx?share=EnNjotrV4F1Gp4RR3KVyXggB2y7v8tz3T2cxcbCqtzL5yA&e=UHQUPT)

---

### 2. Run with Docker

```bash
docker-compose up -d --build
```

Access:
- Frontend: http://localhost
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🐳 VPS Deployment

### Deploy to Internet

```bash
# 1. Download models
scripts/download-models.sh

# 2. Deploy with SSL
scripts/deploy.sh example.com admin@example.com
```

Result: Application live at `https://example.com` (~20 minutes)

---

### Update After Changes

```bash
scripts/restart.sh
```

Result: Latest code deployed (~2-5 minutes)

---

### Stop Application

```bash
scripts/stop.sh
```

---

## 📁 Project Structure

```
image-reconstruction/
├── scripts/
│   ├── deploy.sh           # Deploy to VPS with SSL
│   ├── restart.sh          # Update & restart
│   ├── stop.sh             # Stop services
│   └── download-models.sh  # Download model files
├── backend/                # FastAPI backend
│   └── model/              # Model files (.pth)
├── frontend/               # Static web interface
└── config.json             # Configuration
```

---

## ⚙️ Configuration

Edit `config.json`:

```json
{
  "backend": {
    "port": 8000,
    "model": {
      "device": "auto"
    },
    "upload": {
      "max_size_mb": 20
    }
  },
  "frontend": {
    "backend_url": "http://localhost:8000"
  }
}
```

See **[CONFIG.md](CONFIG.md)** for all options.

---

## 📝 Tech Stack

- **Backend:** Python 3.10+, FastAPI, PyTorch
- **Frontend:** HTML5, JavaScript, CSS3
- **Deployment:** Docker, Docker Compose, Nginx
- **Models:** REAL-ESRGAN, ConvNext REAL-ESRGAN
