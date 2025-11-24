#!/bin/bash

################################################################################
# Quick Update Script - Pull changes from GitHub and restart services
# Usage: ./update.sh
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
echo "  Restart & Update - Pull Latest Changes from GitHub"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed"
    exit 1
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_error "Not a git repository. Please run this from the project root."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed"
    exit 1
fi

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found. Please run deployment first: scripts/deploy.sh"
    exit 1
fi

################################################################################
# Check if application is running
################################################################################
print_info "Checking if application is running..."

if ! docker-compose ps 2>/dev/null | grep -q "Up"; then
    print_error "Application is not running!"
    echo ""
    print_info "Current status:"
    docker-compose ps
    echo ""
    print_warning "Please deploy the application first using: scripts/deploy.sh [domain] [email]"
    exit 1
fi

print_success "Application is running, proceeding with restart..."
echo ""

################################################################################
# Step 1: Check current status
################################################################################
print_info "[1/6] Checking current branch and status..."
CURRENT_BRANCH=$(git branch --show-current)
print_info "Current branch: $CURRENT_BRANCH"

# Check if there are uncommitted changes
if ! git diff-index --quiet HEAD --; then
    print_warning "You have uncommitted local changes!"
    echo ""
    git status --short
    echo ""
    read -p "Continue anyway? Local changes may be overwritten. (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Update cancelled"
        exit 1
    fi

    # Stash local changes
    print_info "Stashing local changes..."
    git stash
    print_success "Local changes stashed"
fi

echo ""

################################################################################
# Step 2: Fetch latest changes
################################################################################
print_info "[2/6] Fetching latest changes from GitHub..."
git fetch origin

# Check if there are updates
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/$CURRENT_BRANCH)

if [ "$LOCAL" = "$REMOTE" ]; then
    print_success "Already up to date! No changes to pull."
    echo ""
    print_info "Current services status:"
    docker-compose ps
    exit 0
fi

print_info "New commits available:"
git log --oneline HEAD..origin/$CURRENT_BRANCH | head -5
echo ""

################################################################################
# Step 3: Pull changes
################################################################################
print_info "[3/6] Pulling latest changes..."
git pull origin $CURRENT_BRANCH
print_success "Code updated successfully"
echo ""

################################################################################
# Step 4: Check if rebuild is needed
################################################################################
print_info "[4/6] Checking if Docker rebuild is needed..."
REBUILD_NEEDED=false

# Check if Dockerfile or requirements changed
if git diff HEAD@{1} HEAD --name-only | grep -qE "Dockerfile|requirements.txt|package.json|docker-compose.yml"; then
    print_warning "Docker configuration or dependencies changed"
    REBUILD_NEEDED=true
fi

# Check if backend code changed
if git diff HEAD@{1} HEAD --name-only | grep -qE "backend/.*\.py"; then
    print_info "Backend code changed"
    REBUILD_NEEDED=true
fi

# Check if frontend code changed
if git diff HEAD@{1} HEAD --name-only | grep -qE "frontend/.*\.(html|js|css)"; then
    print_info "Frontend code changed"
    REBUILD_NEEDED=true
fi

echo ""

################################################################################
# Step 5: Rebuild and restart
################################################################################
if [ "$REBUILD_NEEDED" = true ]; then
    print_info "[5/6] Rebuilding and restarting services..."

    # Show current containers before stopping
    print_info "Current containers:"
    docker-compose ps
    echo ""

    print_info "Building new images..."
    docker-compose build --quiet

    print_info "Restarting services with new build..."
    docker-compose up -d --build

    print_success "Services rebuilt and restarted"
else
    print_info "[5/6] Restarting services (no rebuild needed)..."
    docker-compose restart
    print_success "Services restarted"
fi

echo ""

################################################################################
# Step 6: Verify deployment
################################################################################
print_info "[6/6] Verifying deployment..."
sleep 5

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    print_success "Containers are running"
else
    print_error "Some containers failed to start"
    print_info "Check logs with: docker-compose logs"
    exit 1
fi

# Check backend health
print_info "Checking backend health..."
MAX_RETRIES=6
RETRY=0
while [ $RETRY -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
        print_success "Backend is healthy"
        break
    else
        RETRY=$((RETRY+1))
        if [ $RETRY -lt $MAX_RETRIES ]; then
            sleep 3
        else
            print_warning "Backend health check timed out"
            print_info "Check logs with: docker-compose logs backend"
        fi
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_success "UPDATE COMPLETED SUCCESSFULLY!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_info "Changes pulled and services restarted"
echo ""
echo "Current status:"
docker-compose ps
echo ""
echo "Useful commands:"
echo "  • View logs:        docker-compose logs -f"
echo "  • Check health:     curl http://localhost:8000/api/health"
echo "  • Restart service:  docker-compose restart [backend|frontend]"
echo ""
