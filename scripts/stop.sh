#!/bin/bash

################################################################################
# Stop Script - Stop all running Docker services
# Usage: ./stop.sh
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}→ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Stop Image Reconstruction Application"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed"
    exit 1
fi

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found. Are you in the correct directory?"
    exit 1
fi

################################################################################
# Check if application is running
################################################################################
print_info "Checking application status..."

if ! docker-compose ps | grep -q "Up"; then
    print_warning "Application is not running"
    echo ""
    print_info "Current status:"
    docker-compose ps
    echo ""
    print_info "Nothing to stop. Application is already stopped."
    exit 0
fi

print_success "Application is currently running"
echo ""

################################################################################
# Show current status
################################################################################
print_info "Current running containers:"
docker-compose ps
echo ""

################################################################################
# Stop services
################################################################################
print_info "Stopping all services..."

docker-compose down

print_success "All services stopped successfully"
echo ""

################################################################################
# Verify
################################################################################
print_info "Verifying shutdown..."
sleep 2

if docker-compose ps | grep -q "Up"; then
    print_warning "Some containers are still running"
    docker-compose ps
else
    print_success "All containers stopped"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_success "APPLICATION STOPPED SUCCESSFULLY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To start the application again, run:"
echo "  • For updates: ./restart.sh"
echo "  • Fresh start: ./deploy.sh [domain] [email]"
echo ""
