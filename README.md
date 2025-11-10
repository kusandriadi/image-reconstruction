# Image Reconstruction App

AI-powered image reconstruction using PyTorch REAL-ESRGAN models with a modern web interface.

![BINUS Style UI](https://img.shields.io/badge/UI-BINUS%20Orange-f3931b)
![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)

## 📑 Table of Contents

- [✨ Features](#-features)
- [📚 Platform-Specific Setup Guides](#-platform-specific-setup-guides)
- [📁 Project Structure](#-project-structure)
- [🚀 Quick Start](#-quick-start)
  - [Option 1: Local Development](#option-1-local-development)
  - [Option 2: Docker (Production)](#option-2-docker-production)
    - [Quick Launch with Auto-Check Script](#quick-launch-with-auto-check-script)
    - [Manual Deployment](#manual-deployment)
    - [Access Application](#access-application)
- [🐳 VPS Deployment](#-vps-deployment)
  - [Quick VPS Setup](#quick-vps-setup)
- [⚙️ Configuration](#️-configuration)
  - [Quick Config](#quick-config)
  - [Environment Variables](#environment-variables)
- [🔧 Docker Commands](#-docker-commands)
- [📊 API Endpoints](#-api-endpoints)
- [🎨 UI Features](#-ui-features)
- [🛠️ Troubleshooting](#️-troubleshooting)
  - [Backend won't start](#backend-wont-start)
  - [Frontend shows connection error](#frontend-shows-connection-error)
  - [Model switching not working](#model-switching-not-working)
  - [Out of memory](#out-of-memory)
- [📖 Documentation](#-documentation)
  - [Platform Setup](#platform-setup)
  - [Main Guides](#main-guides)
  - [Component Docs](#component-docs)
  - [Tools](#tools)
- [🔍 Verify Model Switching](#-verify-model-switching)
- [📝 Tech Stack](#-tech-stack)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [🆘 Support](#-support)
- [🎯 Quick Reference](#-quick-reference)

---

## ✨ Features

- 🎨 **Modern UI** - BINUS-themed orange and teal design with drag & drop
- 🤖 **Dual Models** - Choose between ConvNext REAL-ESRGAN or REAL-ESRGAN
- 📊 **Real-time Progress** - Live progress tracking with cancellation support
- 🐳 **Docker Ready** - One-command deployment to production
- ⚡ **Fast API** - Async processing with FastAPI backend
- 🔄 **Auto-reset** - Reset button after completion for easy batch processing

---

## 📚 Platform-Specific Setup Guides

Choose your operating system for detailed setup instructions:

| Platform | Guide | What's Included |
|----------|-------|-----------------|
| 🐧 **Linux** | **[LINUX.md](LINUX.md)** | Ubuntu/Debian/Fedora/Arch setup, Docker installation, Docker Compose installation, troubleshooting |
| 🪟 **Windows** | **[WINDOWS.md](WINDOWS.md)** | Docker Desktop, WSL2 setup, PowerShell/CMD commands, Docker Compose installation, troubleshooting |

These guides include:
- Complete installation steps for Docker and Docker Compose
- Platform-specific commands and troubleshooting
- Python virtual environment setup
- Common issues and solutions

---

## 📁 Project Structure

```
image-reconstruction/
├── backend/              # FastAPI backend → See: backend/README.md
│   ├── app.py           # Main API application
│   ├── services/        # Business logic (jobs, reconstruction)
│   ├── models/          # Model architectures (RRDBNet)
│   └── model/           # Model files (.pth) → See: backend/model/README.md
├── frontend/            # Static web interface → See: frontend/README.md
│   ├── index.html       # Main UI
│   ├── script.js        # Frontend logic
│   └── styles.css       # BINUS-themed styling
├── config.json          # Centralized configuration
├── Dockerfile           # Backend container
├── docker-compose.yml   # Production orchestration
└── deploy.sh           # Automated deployment script
```

**📚 Component Documentation:**
- **[backend/README.md](backend/README.md)** - Backend service setup and API details
- **[frontend/README.md](frontend/README.md)** - Frontend setup and features
- **[backend/model/README.md](backend/model/README.md)** - How to add model files (includes download link)
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete production deployment guide

---

## 🚀 Quick Start

> **💡 For detailed platform-specific instructions**, see:
> - **Linux**: [LINUX.md](LINUX.md) (includes Docker/Docker Compose installation)
> - **Windows**: [WINDOWS.md](WINDOWS.md) (includes Docker Desktop/WSL2 setup)

### Option 1: Local Development

**Requirements:** Python 3.10+

1. **Install dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

2. **Place your models:**
   ```bash
   # Put your .pth files in backend/model/
   # - ConvNext_REAL-ESRGAN.pth
   # - REAL-ESRGAN.pth
   ```
   **See:** [backend/model/README.md](backend/model/README.md) for download link and details

3. **Run the app:**
   ```bash
   # Single command (recommended)
   python run_all.py --reload

   # Or manually:
   # Terminal 1: uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
   # Terminal 2: cd frontend && python -m http.server 5173
   ```

4. **Open browser:** http://localhost:5173

### Option 2: Docker (Production)

**Requirements:** Docker & Docker Compose installed

#### Quick Launch with Auto-Check Script

The easiest way to run with Docker - automatically checks requirements:

**Linux/macOS:**
```bash
chmod +x run-docker.sh
./run-docker.sh
```

**Windows PowerShell:**
```powershell
.\run-docker.ps1
```

These scripts will:
- ✓ Check if Docker is installed
- ✓ Check if Docker Compose is available
- ✓ Verify Docker daemon is running
- ✓ Create necessary directories
- ✓ Build and start containers
- ✓ Show status and access URLs

#### Manual Deployment

**Option A - Using deploy.sh:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Option B - Direct Docker Compose:**
```bash
docker compose up -d --build
# or
docker-compose up -d --build
```

#### Access Application

- Frontend: http://localhost
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

---

## 🐳 VPS Deployment

Deploy to production VPS in 5 minutes - **See:** [DEPLOYMENT.md](DEPLOYMENT.md) for complete guide

### Quick VPS Setup

```bash
# 1. SSH into your VPS
ssh root@your-vps-ip

# 2. Install Docker
curl -fsSL https://get.docker.com | sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. Clone & Deploy
git clone https://github.com/yourusername/image-reconstruction.git
cd image-reconstruction
./deploy.sh

# 4. Configure Firewall
sudo ufw allow 80/tcp && sudo ufw allow 443/tcp && sudo ufw enable
```

Access: `http://your-vps-ip`

---

## ⚙️ Configuration

### Quick Config

Edit `config.json`:

```json
{
  "backend": {
    "port": 8000,
    "model": {
      "path": "backend/model/ConvNext_REAL-ESRGAN.pth",
      "device": "auto"
    },
    "upload": {
      "max_size_mb": 20
    }
  },
  "frontend": {
    "backend_url": "http://localhost:8000",
    "polling": {
      "interval_ms": 800
    }
  }
}
```

### Environment Variables

Override any setting:

```bash
# Backend
export BACKEND_MODEL_DEVICE=cuda
export BACKEND_UPLOAD_MAX_SIZE_MB=50

# Frontend
export FRONTEND_BACKEND_URL=http://yourdomain.com
```

**Full configuration guide:** [CONFIG.md](CONFIG.md)

---

## 🔧 Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart
docker-compose restart

# Update app
git pull
docker-compose up -d --build

# Development mode (with hot-reload)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/jobs` | Create reconstruction job |
| GET | `/api/jobs/{job_id}` | Get job status |
| DELETE | `/api/jobs/{job_id}` | Cancel job |
| GET | `/api/jobs/{job_id}/result` | Download result |
| GET | `/api/health` | Health check |
| GET | `/api/config` | Frontend config |

**API Documentation:** http://localhost:8000/docs (when running)

**See also:** [backend/README.md](backend/README.md) for detailed API information

---

## 🎨 UI Features

- **Model Selection** - Choose between 2 REAL-ESRGAN models
- **Drag & Drop** - Upload images by dragging to the drop zone
- **Real-time Progress** - See reconstruction progress with percentage
- **Cancellation** - Cancel processing at any time
- **Auto Reset** - Reset button appears after completion
- **Download** - Direct download of reconstructed images
- **BINUS Theme** - Professional orange and teal color scheme

**See also:** [frontend/README.md](frontend/README.md) for more details

---

## 🛠️ Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Verify models exist
ls -lh backend/model/

# Check permissions
chmod 755 backend/data/uploads backend/data/outputs
```

### Frontend shows connection error
```bash
# Check backend is running
curl http://localhost:8000/api/health

# Update config.json with correct backend URL
```

### Model switching not working
```bash
# Verify models are different
python verify_models.py

# Check backend logs for model switching
docker-compose logs -f backend | grep "🎯\|🔄\|⚙️"
```

### Out of memory
```bash
# Check memory usage
docker stats

# Solution: Upgrade VPS RAM or use CPU mode
```

---

## 📖 Documentation

### Platform Setup
- **[LINUX.md](LINUX.md)** - Complete Linux setup guide (Ubuntu/Debian/Fedora/Arch)
- **[WINDOWS.md](WINDOWS.md)** - Complete Windows setup guide (Docker Desktop, WSL2)

### Main Guides
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete production deployment guide (SSL, security, backups)
- **[CONFIG.md](CONFIG.md)** - Detailed configuration reference

### Component Docs
- **[backend/README.md](backend/README.md)** - Backend API setup and environment variables
- **[frontend/README.md](frontend/README.md)** - Frontend setup and features
- **[backend/model/README.md](backend/model/README.md)** - Model files download link and format

### Tools
- **[verify_models.py](verify_models.py)** - Verify model files are different

---

## 🔍 Verify Model Switching

Check if your two models are actually different:

```bash
python verify_models.py
```

Watch backend logs for model selection:

```bash
# Look for these indicators:
# 🎯 Job started with model selection
# 📦 Using current model
# 🔄 MODEL SWITCH (when changing models)
# ⚙️ LOADING MODEL
# ✅ Model loaded successfully
```

---

## 📝 Tech Stack

- **Backend:** FastAPI, PyTorch, Uvicorn
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Models:** REAL-ESRGAN, ConvNext-ESRGAN (RRDBNet architecture)
- **Deployment:** Docker, Docker Compose, Nginx
- **Styling:** BINUS color scheme (Orange #f3931b, Teal #1b9ad7)

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📄 License

This project is for educational and research purposes.

---

## 🆘 Support

- **Issues:** Check backend logs with `docker-compose logs -f backend`
- **Questions:** See documentation in [DEPLOYMENT.md](DEPLOYMENT.md)
- **Model Help:** Run `python verify_models.py` or check [backend/model/README.md](backend/model/README.md)

---

## 🎯 Quick Reference

```bash
# Local Development
python run_all.py --reload

# Docker Production
./deploy.sh

# VPS Deployment
ssh root@vps-ip
curl -fsSL https://get.docker.com | sh
git clone <repo> && cd image-reconstruction
./deploy.sh

# Logs
docker-compose logs -f

# Update
git pull && docker-compose up -d --build
```

---

**Made with ❤️ using BINUS color theme**
