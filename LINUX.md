# Linux Setup Guide

Complete setup guide for running Image Reconstruction App on Linux systems.

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
  - [Method 1: Local Development](#method-1-local-development-python)
  - [Method 2: Docker](#method-2-docker-production)
- [Installing Docker](#installing-docker)
- [Installing Docker Compose](#installing-docker-compose)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/image-reconstruction.git
cd image-reconstruction

# Option 1: Run with Docker Auto-Check Script (easiest)
chmod +x run-docker.sh
./run-docker.sh

# Option 2: Run with deploy script
./deploy.sh

# Option 3: Run locally with Python
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python run_all.py --reload
```

**What's the difference?**
- **run-docker.sh**: Checks if Docker/Docker Compose are installed, provides helpful error messages
- **deploy.sh**: Assumes Docker is installed, runs directly
- **Python**: Runs locally without Docker

---

## Prerequisites

### For Local Development
- **Python**: 3.10 or higher
- **pip**: Python package manager
- **Git**: Version control

```bash
# Check versions
python3 --version
pip3 --version
git --version
```

### For Docker Deployment
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

```bash
# Check versions
docker --version
docker compose version
```

---

## Installation Methods

### Method 1: Local Development (Python)

#### Step 1: Install Python Dependencies

```bash
# Install Python 3.10+ (if not installed)
# Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip

# Fedora/RHEL/CentOS
sudo dnf install python3.10 python3-pip

# Arch Linux
sudo pacman -S python python-pip
```

#### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# You should see (.venv) in your prompt
```

#### Step 3: Install Application Dependencies

```bash
# Install requirements
pip install -r backend/requirements.txt

# Verify installation
pip list
```

#### Step 4: Add Model Files

```bash
# Create model directory (if not exists)
mkdir -p backend/model

# Download models from the link in backend/model/README.md
# Place .pth files in backend/model/
# - ConvNext_REAL-ESRGAN.pth
# - REAL-ESRGAN.pth
```

See [backend/model/README.md](backend/model/README.md) for download link.

#### Step 5: Run the Application

```bash
# Single command (runs both backend and frontend)
python run_all.py --reload

# Or manually in separate terminals:
# Terminal 1 - Backend
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
python3 -m http.server 5173
```

#### Step 6: Access Application

Open browser: **http://localhost:5173**

---

### Method 2: Docker (Production)

#### Easy Way: Using Auto-Check Script

The **run-docker.sh** script automatically checks all requirements and starts the application:

```bash
# Make script executable
chmod +x run-docker.sh

# Run the script
./run-docker.sh
```

The script will:
1. Check if Docker is installed (provides installation commands if missing)
2. Check if Docker daemon is running
3. Check if Docker Compose is available
4. Verify model files exist
5. Create necessary directories
6. Build and start containers
7. Display access URLs

**If the script finds any issues, it will tell you exactly how to fix them!**

---

#### Manual Way: Step-by-Step

If you prefer manual setup:

#### Step 1: Install Docker

If Docker is not installed, see [Installing Docker](#installing-docker) section below.

#### Step 2: Install Docker Compose

If Docker Compose is not installed, see [Installing Docker Compose](#installing-docker-compose) section below.

#### Step 3: Add Model Files

```bash
# Create model directory (if not exists)
mkdir -p backend/model

# Download and place model files
# See backend/model/README.md for download link
```

#### Step 4: Deploy with Docker

```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh

# Or manually
docker compose up -d --build
```

#### Step 5: Access Application

- **Frontend**: http://localhost
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

---

## Installing Docker

### Ubuntu/Debian

```bash
# Update package index
sudo apt update

# Install prerequisites
sudo apt install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
sudo docker run hello-world
```

### Fedora/RHEL/CentOS

```bash
# Install prerequisites
sudo dnf -y install dnf-plugins-core

# Add Docker repository
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo

# Install Docker Engine
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
sudo docker run hello-world
```

### Arch Linux

```bash
# Install Docker
sudo pacman -S docker docker-compose

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
sudo docker run hello-world
```

### Add Your User to Docker Group (Optional)

This allows running Docker without `sudo`:

```bash
# Add current user to docker group
sudo usermod -aG docker $USER

# Log out and log back in, or run:
newgrp docker

# Verify you can run docker without sudo
docker run hello-world
```

---

## Installing Docker Compose

### Method 1: Docker Compose Plugin (Recommended)

Docker Compose v2 is included with modern Docker installations as a plugin.

```bash
# Already installed with Docker using the commands above
# Verify installation
docker compose version
```

### Method 2: Standalone Binary

If you need the standalone binary:

```bash
# Download latest version
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)

sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

**Note**: With standalone binary, use `docker-compose` (with hyphen) instead of `docker compose`.

### Method 3: Using Package Manager

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install docker-compose-plugin
```

#### Fedora
```bash
sudo dnf install docker-compose-plugin
```

#### Arch Linux
```bash
sudo pacman -S docker-compose
```

---

## Running the Application

### Using Docker Compose Plugin

```bash
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

### Using Standalone Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Update application
git pull
docker-compose up -d --build
```

### Managing Services

```bash
# View running containers
docker ps

# View all containers
docker ps -a

# Stop all containers
docker compose down
# or
docker-compose down

# Remove all containers and volumes
docker compose down -v

# View logs for specific service
docker compose logs backend
docker compose logs frontend

# Execute command in running container
docker compose exec backend bash
```

---

## Troubleshooting

### Permission Denied Errors

```bash
# If you get "permission denied" when running docker
sudo usermod -aG docker $USER
newgrp docker

# For file permission issues
sudo chmod -R 755 backend/data/uploads backend/data/outputs
sudo chown -R $USER:$USER backend/data
```

### Port Already in Use

```bash
# Check what's using port 80
sudo lsof -i :80

# Check what's using port 8000
sudo lsof -i :8000

# Kill process using port
sudo kill -9 <PID>

# Or change ports in config.json and docker-compose.yml
```

### Docker Service Not Running

```bash
# Start Docker service
sudo systemctl start docker

# Enable Docker to start on boot
sudo systemctl enable docker

# Check Docker status
sudo systemctl status docker
```

### Cannot Connect to Docker Daemon

```bash
# Start Docker daemon
sudo systemctl start docker

# Check if Docker socket has correct permissions
sudo chmod 666 /var/run/docker.sock

# Or add user to docker group (recommended)
sudo usermod -aG docker $USER
newgrp docker
```

### Out of Disk Space

```bash
# Remove unused containers, images, networks
docker system prune -a

# Remove unused volumes
docker volume prune

# Check disk usage
docker system df
```

### Container Exits Immediately

```bash
# View container logs
docker compose logs backend

# Check if models exist
ls -lh backend/model/

# Verify models are not empty
du -h backend/model/*.pth
```

### Python Module Not Found

```bash
# Rebuild containers
docker compose down
docker compose up -d --build

# For local development, reinstall requirements
source .venv/bin/activate
pip install -r backend/requirements.txt --force-reinstall
```

### Firewall Blocking Ports

```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 80/tcp
sudo ufw allow 8000/tcp
sudo ufw enable

# firewalld (Fedora/RHEL/CentOS)
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# iptables
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
```

### GPU Not Detected (CUDA)

```bash
# Install nvidia-docker2 for GPU support
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt update
sudo apt install -y nvidia-docker2
sudo systemctl restart docker

# Verify GPU access
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

### Backend Shows 404 Errors

```bash
# Check nginx configuration
docker compose exec frontend cat /etc/nginx/conf.d/default.conf

# Restart nginx
docker compose restart frontend

# Check backend is running
curl http://localhost:8000/api/health
```

---

## Quick Reference Commands

### Docker

```bash
# Start application
docker compose up -d

# Stop application
docker compose down

# View logs
docker compose logs -f

# Restart services
docker compose restart

# Update application
git pull && docker compose up -d --build

# Shell into backend container
docker compose exec backend bash

# Check resource usage
docker stats
```

### Local Development

```bash
# Activate virtual environment
source .venv/bin/activate

# Deactivate virtual environment
deactivate

# Run application
python run_all.py --reload

# Install new dependencies
pip install -r backend/requirements.txt

# Verify models
python verify_models.py
```

### System Management

```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
top
htop  # if installed

# Check listening ports
sudo netstat -tulpn
sudo ss -tulpn
```

---

## Additional Resources

- **Main Documentation**: [README.md](README.md)
- **Windows Guide**: [WINDOWS.md](WINDOWS.md)
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Configuration Guide**: [CONFIG.md](CONFIG.md)
- **Backend Documentation**: [backend/README.md](backend/README.md)
- **Frontend Documentation**: [frontend/README.md](frontend/README.md)
- **Model Setup**: [backend/model/README.md](backend/model/README.md)

---

## Support

For issues specific to Linux:

1. **Check logs**: `docker compose logs -f` or check terminal output
2. **Verify Docker**: `docker --version` and `docker compose version`
3. **Check permissions**: Ensure user is in docker group
4. **Review firewall**: Make sure ports 80 and 8000 are open
5. **System resources**: Check disk space and memory with `df -h` and `free -h`

---

**Made with ❤️ using BINUS color theme**
