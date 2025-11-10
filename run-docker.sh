#!/bin/bash

# Image Reconstruction App - Docker Launcher Script (Linux/macOS)
# This script checks for Docker and Docker Compose, then runs the application

set -e

echo "============================================================"
echo "  Image Reconstruction App - Docker Launcher"
echo "============================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if Docker is installed
echo "Step 1: Checking Docker installation..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    print_success "Docker is installed: $DOCKER_VERSION"
else
    print_error "Docker is not installed!"
    echo ""
    print_info "Please install Docker first:"
    echo ""
    echo "Ubuntu/Debian:"
    echo "  curl -fsSL https://get.docker.com | sh"
    echo ""
    echo "Or visit: https://docs.docker.com/engine/install/"
    echo ""
    print_info "After installing, run this script again."
    echo ""
    print_info "For detailed instructions, see: LINUX.md"
    exit 1
fi
echo ""

# Check if Docker daemon is running
echo "Step 2: Checking Docker daemon..."
if docker info &> /dev/null; then
    print_success "Docker daemon is running"
else
    print_error "Docker daemon is not running!"
    echo ""
    print_info "Start Docker with:"
    echo "  sudo systemctl start docker"
    echo ""
    print_info "Or add your user to the docker group:"
    echo "  sudo usermod -aG docker \$USER"
    echo "  newgrp docker"
    exit 1
fi
echo ""

# Check if Docker Compose is installed
echo "Step 3: Checking Docker Compose..."
COMPOSE_CMD=""

# Try docker compose (v2 - plugin)
if docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version)
    COMPOSE_CMD="docker compose"
    print_success "Docker Compose v2 is installed: $COMPOSE_VERSION"
# Try docker-compose (v1 - standalone)
elif command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    COMPOSE_CMD="docker-compose"
    print_success "Docker Compose v1 is installed: $COMPOSE_VERSION"
else
    print_error "Docker Compose is not installed!"
    echo ""
    print_info "Please install Docker Compose:"
    echo ""
    echo "Method 1 - Install plugin (recommended):"
    echo "  sudo apt install docker-compose-plugin"
    echo ""
    echo "Method 2 - Download binary:"
    echo "  sudo curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
    echo "  sudo chmod +x /usr/local/bin/docker-compose"
    echo ""
    print_info "For detailed instructions, see: LINUX.md"
    exit 1
fi
echo ""

# Check if model files exist
echo "Step 4: Checking model files..."
if [ -f "backend/model/ConvNext_REAL-ESRGAN.pth" ] || [ -f "backend/model/REAL-ESRGAN.pth" ]; then
    print_success "Model files found"
else
    print_warning "Model files not found in backend/model/"
    echo ""
    print_info "Please download model files first:"
    echo "  See: backend/model/README.md for download link"
    echo ""
    read -p "Continue without models? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Exiting. Please add model files and run again."
        exit 1
    fi
fi
echo ""

# Create necessary directories
echo "Step 5: Creating directories..."
mkdir -p backend/data/uploads backend/data/outputs
print_success "Directories created"
echo ""

# Build and start containers
echo "Step 6: Building and starting Docker containers..."
echo ""
print_info "Running: $COMPOSE_CMD up -d --build"
echo ""

if $COMPOSE_CMD up -d --build; then
    print_success "Docker containers started successfully!"
else
    print_error "Failed to start Docker containers"
    echo ""
    print_info "Check logs with:"
    echo "  $COMPOSE_CMD logs -f"
    exit 1
fi
echo ""

# Wait a moment for containers to start
echo "Waiting for services to start..."
sleep 3
echo ""

# Check container status
echo "============================================================"
echo "  Container Status"
echo "============================================================"
$COMPOSE_CMD ps
echo ""

# Display access information
echo "============================================================"
echo "  🎉 Application Started Successfully!"
echo "============================================================"
echo ""
print_success "Frontend: http://localhost"
print_success "Backend API: http://localhost:8000"
print_success "API Docs: http://localhost:8000/docs"
print_success "Health Check: http://localhost:8000/api/health"
echo ""
echo "============================================================"
echo "  Useful Commands"
echo "============================================================"
echo ""
echo "View logs:"
echo "  $COMPOSE_CMD logs -f"
echo ""
echo "Stop services:"
echo "  $COMPOSE_CMD down"
echo ""
echo "Restart services:"
echo "  $COMPOSE_CMD restart"
echo ""
echo "View running containers:"
echo "  docker ps"
echo ""
echo "============================================================"
echo ""
print_info "Press Ctrl+C to view logs, or close this terminal"
echo ""

# Ask if user wants to view logs
read -p "View logs now? (Y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo ""
    print_info "Showing logs (Press Ctrl+C to exit)..."
    echo ""
    $COMPOSE_CMD logs -f
fi
