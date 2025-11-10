# Windows Setup Guide

Complete setup guide for running Image Reconstruction App on Windows systems.

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
  - [Method 1: Local Development](#method-1-local-development-python)
  - [Method 2: Docker Desktop](#method-2-docker-desktop-production)
  - [Method 3: WSL2 + Docker](#method-3-wsl2--docker-advanced)
- [Installing Docker Desktop](#installing-docker-desktop)
- [Installing Docker Compose](#installing-docker-compose)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### PowerShell (Recommended)

```powershell
# Clone repository
git clone https://github.com/yourusername/image-reconstruction.git
cd image-reconstruction

# Option 1: Run with Docker Auto-Check Script (easiest)
.\run-docker.ps1

# Option 2: Run with Docker Desktop directly
docker compose up -d --build

# Option 3: Run locally with Python
python -m venv .venv
.\.venv\Scripts\activate
pip install -r backend\requirements.txt
python run_all.py --reload
```

**What's the difference?**
- **run-docker.ps1**: Checks if Docker Desktop is installed and running, provides helpful error messages
- **docker compose**: Assumes Docker Desktop is running, executes directly
- **Python**: Runs locally without Docker

### Command Prompt (CMD)

```cmd
# Clone repository
git clone https://github.com/yourusername/image-reconstruction.git
cd image-reconstruction

# Run locally with Python
python -m venv .venv
.venv\Scripts\activate
pip install -r backend\requirements.txt
python run_all.py --reload
```

**Note:** For Docker on CMD, use PowerShell instead or run `docker compose up -d --build` directly

---

## Prerequisites

### For Local Development
- **Python**: 3.10 or higher ([Download](https://www.python.org/downloads/))
- **pip**: Python package manager (included with Python)
- **Git**: Version control ([Download](https://git-scm.com/download/win))

```powershell
# Check versions (PowerShell)
python --version
pip --version
git --version
```

```cmd
# Check versions (CMD)
python --version
pip --version
git --version
```

### For Docker Deployment
- **Docker Desktop**: 4.0+ ([Download](https://www.docker.com/products/docker-desktop))
- **WSL2**: Windows Subsystem for Linux 2 (for Docker Desktop)
- **Windows 10/11**: 64-bit Pro, Enterprise, or Education (Build 19041+)

```powershell
# Check Windows version
winver

# Check WSL2
wsl --list --verbose
```

---

## Installation Methods

### Method 1: Local Development (Python)

#### Step 1: Install Python

1. Download Python 3.10+ from https://www.python.org/downloads/
2. **Important**: Check "Add Python to PATH" during installation
3. Verify installation:

```powershell
python --version
pip --version
```

#### Step 2: Create Virtual Environment

**PowerShell:**
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# You should see (.venv) in your prompt
```

**Command Prompt (CMD):**
```cmd
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate.bat

# You should see (.venv) in your prompt
```

#### Step 3: Install Application Dependencies

```powershell
# Install requirements
pip install -r backend\requirements.txt

# Verify installation
pip list
```

#### Step 4: Add Model Files

```powershell
# Create model directory (if not exists)
New-Item -ItemType Directory -Force -Path backend\model

# Download models from the link in backend\model\README.md
# Place .pth files in backend\model\
# - ConvNext_REAL-ESRGAN.pth
# - REAL-ESRGAN.pth
```

See [backend/model/README.md](backend/model/README.md) for download link.

#### Step 5: Run the Application

```powershell
# Single command (runs both backend and frontend)
python run_all.py --reload

# Or manually in separate terminals:
# Terminal 1 - Backend
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
python -m http.server 5173
```

#### Step 6: Access Application

Open browser: **http://localhost:5173**

---

### Method 2: Docker Desktop (Production)

#### Easy Way: Using Auto-Check Script

The **run-docker.ps1** script automatically checks all requirements and starts the application:

```powershell
# Run the script
.\run-docker.ps1
```

The script will:
1. Check if Docker Desktop is installed (provides installation link if missing)
2. Check if Docker daemon is running (tells you to start Docker Desktop if not)
3. Check if Docker Compose is available
4. Verify model files exist
5. Create necessary directories
6. Build and start containers
7. Display access URLs

**If the script finds any issues, it will tell you exactly how to fix them!**

---

#### Manual Way: Step-by-Step

If you prefer manual setup:

#### Step 1: Install WSL2

Docker Desktop requires WSL2 on Windows.

```powershell
# Run as Administrator

# Enable WSL
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Enable Virtual Machine Platform
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart your computer
Restart-Computer

# After restart, set WSL2 as default
wsl --set-default-version 2

# Install Ubuntu from Microsoft Store (optional but recommended)
# Search "Ubuntu" in Microsoft Store
```

#### Step 2: Install Docker Desktop

See [Installing Docker Desktop](#installing-docker-desktop) section below.

#### Step 3: Add Model Files

```powershell
# Create model directory (if not exists)
New-Item -ItemType Directory -Force -Path backend\model

# Download and place model files
# See backend\model\README.md for download link
```

#### Step 4: Deploy with Docker

```powershell
# Using Docker Compose (included with Docker Desktop)
docker compose up -d --build

# Or use the deploy script (in Git Bash or WSL)
bash deploy.sh
```

#### Step 5: Access Application

- **Frontend**: http://localhost
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

---

### Method 3: WSL2 + Docker (Advanced)

For advanced users who want to run Docker inside WSL2.

#### Step 1: Install WSL2 and Ubuntu

```powershell
# Run as Administrator
wsl --install -d Ubuntu

# Restart computer if prompted
# Set up Ubuntu username and password when prompted
```

#### Step 2: Install Docker in WSL2

```bash
# Inside WSL2 Ubuntu terminal

# Update packages
sudo apt update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin

# Start Docker
sudo service docker start

# Verify installation
docker --version
docker compose version
```

#### Step 3: Clone and Run

```bash
# Inside WSL2 terminal
cd ~
git clone https://github.com/yourusername/image-reconstruction.git
cd image-reconstruction

# Add model files to backend/model/

# Deploy
chmod +x deploy.sh
./deploy.sh
```

---

## Installing Docker Desktop

### System Requirements

- **Windows 10/11**: 64-bit Pro, Enterprise, or Education
- **Build**: 19041 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Virtualization**: Must be enabled in BIOS

### Installation Steps

#### Step 1: Check Virtualization

```powershell
# Check if virtualization is enabled
Get-ComputerInfo | Select-Object -Property "HyperV*"

# Or use Task Manager > Performance > CPU
# Look for "Virtualization: Enabled"
```

If disabled, enable it in BIOS settings (varies by manufacturer).

#### Step 2: Download Docker Desktop

1. Visit https://www.docker.com/products/docker-desktop
2. Click "Download for Windows"
3. Run the installer (Docker Desktop Installer.exe)

#### Step 3: Install Docker Desktop

1. Run the installer
2. **Check** "Use WSL 2 instead of Hyper-V" (recommended)
3. Follow the installation wizard
4. Restart your computer when prompted

#### Step 4: Start Docker Desktop

1. Launch Docker Desktop from Start Menu
2. Accept the service agreement
3. Wait for Docker to start (whale icon in system tray should be steady)

#### Step 5: Verify Installation

```powershell
# Check Docker version
docker --version

# Check Docker Compose version
docker compose version

# Run test container
docker run hello-world
```

### Configuration

```powershell
# Open Docker Desktop settings
# 1. Right-click Docker icon in system tray
# 2. Click "Settings"

# Recommended settings:
# - General > Use WSL 2 based engine: ✓
# - Resources > WSL Integration: Enable for Ubuntu
# - Resources > Advanced: Adjust CPU/Memory as needed
```

---

## Installing Docker Compose

### Docker Compose with Docker Desktop

Docker Compose is **included** with Docker Desktop for Windows. No separate installation needed.

```powershell
# Verify Docker Compose is installed
docker compose version

# Should show: Docker Compose version v2.x.x
```

### Using Docker Compose

With Docker Desktop, use the `docker compose` command (with space, not hyphen):

```powershell
# Correct (Docker Compose v2 - included with Docker Desktop)
docker compose up -d
docker compose down
docker compose logs -f

# Legacy (Docker Compose v1 - standalone binary)
docker-compose up -d
docker-compose down
docker-compose logs -f
```

### Installing Standalone Docker Compose (Legacy)

If you need the standalone `docker-compose` binary:

#### Using Chocolatey

```powershell
# Install Chocolatey first (if not installed)
# Run as Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Docker Compose
choco install docker-compose

# Verify installation
docker-compose --version
```

#### Manual Installation

```powershell
# Download latest version
# Visit: https://github.com/docker/compose/releases
# Download docker-compose-Windows-x86_64.exe

# Rename to docker-compose.exe
# Place in a directory in your PATH (e.g., C:\Program Files\Docker\cli-plugins\)

# Verify installation
docker-compose --version
```

---

## Running the Application

### Using Docker Desktop

```powershell
# Start services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Restart services
docker compose restart

# Update application
git pull
docker compose up -d --build
```

### Managing Services

```powershell
# View running containers
docker ps

# View all containers
docker ps -a

# Stop all containers
docker compose down

# Remove all containers and volumes
docker compose down -v

# View logs for specific service
docker compose logs backend
docker compose logs frontend

# Execute command in running container
docker compose exec backend bash
```

### Using Local Python

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1  # PowerShell
# or
.venv\Scripts\activate.bat     # CMD

# Run application
python run_all.py --reload

# Deactivate virtual environment
deactivate
```

---

## Troubleshooting

### Docker Desktop Won't Start

#### WSL2 Installation Issues

```powershell
# Run as Administrator

# Check WSL version
wsl --list --verbose

# Update WSL
wsl --update

# Set WSL2 as default
wsl --set-default-version 2

# Restart WSL
wsl --shutdown
```

#### Virtualization Not Enabled

1. Restart computer and enter BIOS/UEFI
2. Enable virtualization (Intel VT-x or AMD-V)
3. Save and exit
4. Restart Docker Desktop

#### Hyper-V Issues

```powershell
# Run as Administrator

# Enable Hyper-V
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

# Restart computer
Restart-Computer
```

### Port Already in Use

```powershell
# Check what's using port 80
netstat -ano | findstr :80

# Check what's using port 8000
netstat -ano | findstr :8000

# Kill process by PID
taskkill /PID <PID> /F

# Or change ports in config.json and docker-compose.yml
```

### Python Not Found

```powershell
# Add Python to PATH manually
# 1. Search "Environment Variables" in Start Menu
# 2. Edit "Path" in System Variables
# 3. Add: C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python310
# 4. Add: C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python310\Scripts
# 5. Restart terminal
```

### PowerShell Execution Policy Error

```powershell
# Allow running scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run specific script
PowerShell -ExecutionPolicy Bypass -File .\script.ps1
```

### Virtual Environment Won't Activate

**PowerShell:**
```powershell
# Set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Try activating again
.\.venv\Scripts\Activate.ps1
```

**CMD:**
```cmd
# Use .bat file instead
.venv\Scripts\activate.bat
```

### Docker Compose Command Not Found

```powershell
# Make sure Docker Desktop is running
# Check system tray for Docker whale icon

# Use docker compose (with space) instead of docker-compose
docker compose version

# If docker compose doesn't work, restart Docker Desktop
```

### File Sharing Issues

1. Open Docker Desktop Settings
2. Go to Resources > File Sharing
3. Add your project directory (e.g., `D:\work\image-reconstruction`)
4. Click "Apply & Restart"

### WSL2 Kernel Update Required

Download and install from:
https://aka.ms/wsl2kernel

Then restart Docker Desktop.

### Container Exits Immediately

```powershell
# View container logs
docker compose logs backend

# Check if models exist
dir backend\model\

# Verify models are not empty
dir backend\model\*.pth
```

### Python Module Not Found

```powershell
# Rebuild containers
docker compose down
docker compose up -d --build

# For local development, reinstall requirements
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt --force-reinstall
```

### Firewall Blocking Ports

1. Search "Windows Defender Firewall" in Start Menu
2. Click "Advanced settings"
3. Click "Inbound Rules" > "New Rule"
4. Select "Port" > Next
5. Select "TCP" and enter port 80, 8000
6. Allow the connection
7. Apply to all profiles

Or use PowerShell:

```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "Docker App" -Direction Inbound -Protocol TCP -LocalPort 80,8000 -Action Allow
```

### Out of Disk Space

```powershell
# Remove unused containers, images, networks
docker system prune -a

# Remove unused volumes
docker volume prune

# Check disk usage
docker system df
```

### Line Ending Issues (Git)

```powershell
# Configure Git to handle line endings
git config --global core.autocrlf true

# If scripts fail, convert line endings
# Install dos2unix (via Git Bash or WSL)
dos2unix deploy.sh
```

---

## Quick Reference Commands

### Docker Desktop

```powershell
# Start application
docker compose up -d

# Stop application
docker compose down

# View logs
docker compose logs -f

# Restart services
docker compose restart

# Update application
git pull
docker compose up -d --build

# Shell into backend container
docker compose exec backend bash

# Check resource usage
docker stats
```

### Local Development (PowerShell)

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Deactivate virtual environment
deactivate

# Run application
python run_all.py --reload

# Install new dependencies
pip install -r backend\requirements.txt

# Verify models
python verify_models.py
```

### System Management

```powershell
# Check disk space
Get-PSDrive

# Check memory usage
Get-Process | Sort-Object -Property WS -Descending | Select-Object -First 10

# Check listening ports
netstat -ano | findstr LISTENING

# Check Windows version
winver
systeminfo
```

---

## WSL2 Tips

### Access Windows Files from WSL2

```bash
# Windows C: drive
cd /mnt/c/Users/YourUsername

# Your project
cd /mnt/d/work/image-reconstruction
```

### Access WSL2 Files from Windows

In File Explorer, go to:
```
\\wsl$\Ubuntu\home\yourusername
```

### Run WSL Commands from PowerShell

```powershell
# Run Linux command from PowerShell
wsl ls -la

# Run Docker in WSL from PowerShell
wsl docker ps

# Open WSL terminal
wsl
```

---

## Additional Resources

- **Main Documentation**: [README.md](README.md)
- **Linux Guide**: [LINUX.md](LINUX.md)
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Configuration Guide**: [CONFIG.md](CONFIG.md)
- **Backend Documentation**: [backend/README.md](backend/README.md)
- **Frontend Documentation**: [frontend/README.md](frontend/README.md)
- **Model Setup**: [backend/model/README.md](backend/model/README.md)

### External Links

- **Docker Desktop**: https://www.docker.com/products/docker-desktop
- **Python for Windows**: https://www.python.org/downloads/
- **Git for Windows**: https://git-scm.com/download/win
- **WSL2 Documentation**: https://docs.microsoft.com/windows/wsl/
- **Docker on Windows**: https://docs.docker.com/desktop/windows/

---

## Support

For issues specific to Windows:

1. **Check Docker Desktop**: Ensure it's running (whale icon in system tray)
2. **Check WSL2**: Run `wsl --list --verbose` in PowerShell
3. **Check logs**: `docker compose logs -f` or check terminal output
4. **Verify Python**: Ensure it's in PATH with `python --version`
5. **Check firewall**: Make sure ports 80 and 8000 are allowed
6. **Restart**: Try restarting Docker Desktop or your computer

---

**Made with ❤️ using BINUS color theme**
