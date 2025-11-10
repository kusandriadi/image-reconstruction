#!/bin/bash
# Quick deployment script for Image Reconstruction app

set -e  # Exit on error

echo "========================================="
echo "Image Reconstruction - Deployment Script"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed!${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed!${NC}"
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"
echo ""

# Check if model files exist
echo "Checking for model files..."
if [ ! -f "backend/model/ConvNext_REAL-ESRGAN.pth" ] && [ ! -f "backend/model/REAL-ESRGAN.pth" ]; then
    echo -e "${YELLOW}Warning: No model files found in backend/model/${NC}"
    echo "Please ensure your .pth model files are in backend/model/ directory"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ Model files found${NC}"
fi
echo ""

# Create necessary directories
echo "Creating data directories..."
mkdir -p backend/data/uploads
mkdir -p backend/data/outputs
chmod 755 backend/data/uploads backend/data/outputs
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}No .env file found. Using .env.example as template...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env from .env.example${NC}"
        echo -e "${YELLOW}Please edit .env file with your settings before production use!${NC}"
    fi
fi
echo ""

# Ask deployment mode
echo "Select deployment mode:"
echo "1) Development (with auto-reload)"
echo "2) Production (optimized)"
read -p "Enter choice (1 or 2): " mode

if [ "$mode" == "1" ]; then
    echo ""
    echo "Starting in DEVELOPMENT mode..."
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
elif [ "$mode" == "2" ]; then
    echo ""
    echo "Starting in PRODUCTION mode..."
    docker-compose up -d --build
else
    echo -e "${RED}Invalid choice. Exiting.${NC}"
    exit 1
fi

echo ""
echo "Waiting for services to start..."
sleep 5

# Check if services are running
echo ""
echo "Checking service status..."
docker-compose ps

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Services running:"
echo "  • Frontend: http://localhost (port 80)"
echo "  • Backend API: http://localhost:8000"
echo "  • Health Check: http://localhost:8000/api/health"
echo ""
echo "Useful commands:"
echo "  • View logs: docker-compose logs -f"
echo "  • Stop services: docker-compose down"
echo "  • Restart: docker-compose restart"
echo ""
echo -e "${YELLOW}Note: If deploying to production, don't forget to:${NC}"
echo "  1. Configure your domain name in config.json"
echo "  2. Set up SSL/HTTPS certificates"
echo "  3. Configure firewall rules"
echo "  4. Update CORS settings for your domain"
echo ""
