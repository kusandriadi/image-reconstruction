#!/bin/bash

################################################################################
# Logs Script - View live application logs
# Usage: ./logs.sh [service]
#
# Examples:
#   ./logs.sh          # View all logs (backend + frontend)
#   ./logs.sh backend  # View backend logs only
#   ./logs.sh frontend # View frontend logs only
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}→ $1${NC}"
}

print_header() {
    echo -e "${CYAN}$1${NC}"
}

################################################################################
# Check if docker-compose is installed
################################################################################
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed"
    exit 1
fi

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found"
    print_info "Run this script from the project root directory"
    exit 1
fi

################################################################################
# Parse arguments
################################################################################
SERVICE="${1:-}"

# Validate service name if provided
if [ -n "$SERVICE" ] && [ "$SERVICE" != "backend" ] && [ "$SERVICE" != "frontend" ]; then
    print_error "Invalid service name: $SERVICE"
    echo ""
    echo "Usage: $0 [service]"
    echo ""
    echo "Available services:"
    echo "  backend   - View backend logs only"
    echo "  frontend  - View frontend logs only"
    echo "  (none)    - View all logs"
    echo ""
    exit 1
fi

################################################################################
# Display logs
################################################################################
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -n "$SERVICE" ]; then
    print_header "  Viewing $SERVICE logs (Press Ctrl+C to exit)"
else
    print_header "  Viewing all logs (Press Ctrl+C to exit)"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Follow logs
if [ -n "$SERVICE" ]; then
    docker-compose logs -f "$SERVICE"
else
    docker-compose logs -f
fi
