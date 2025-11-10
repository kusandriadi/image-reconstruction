# Image Reconstruction App - Docker Launcher Script (Windows PowerShell)
# This script checks for Docker and Docker Compose, then runs the application

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Image Reconstruction App - Docker Launcher" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Function to print colored messages
function Print-Success {
    param([string]$Message)
    Write-Host "✓ " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Print-Error {
    param([string]$Message)
    Write-Host "✗ " -ForegroundColor Red -NoNewline
    Write-Host $Message
}

function Print-Warning {
    param([string]$Message)
    Write-Host "⚠ " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

function Print-Info {
    param([string]$Message)
    Write-Host "ℹ " -ForegroundColor Blue -NoNewline
    Write-Host $Message
}

# Check if Docker is installed
Write-Host "Step 1: Checking Docker installation..." -ForegroundColor White
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Print-Success "Docker is installed: $dockerVersion"
    } else {
        throw "Docker not found"
    }
} catch {
    Print-Error "Docker is not installed or not in PATH!"
    Write-Host ""
    Print-Info "Please install Docker Desktop for Windows:"
    Write-Host ""
    Write-Host "  1. Download from: https://www.docker.com/products/docker-desktop"
    Write-Host "  2. Install and restart your computer"
    Write-Host "  3. Start Docker Desktop from Start Menu"
    Write-Host ""
    Print-Info "For detailed instructions, see: WINDOWS.md"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Check if Docker Desktop is running
Write-Host "Step 2: Checking Docker daemon..." -ForegroundColor White
try {
    $dockerInfo = docker info 2>$null
    if ($LASTEXITCODE -eq 0) {
        Print-Success "Docker daemon is running"
    } else {
        throw "Docker daemon not running"
    }
} catch {
    Print-Error "Docker Desktop is not running!"
    Write-Host ""
    Print-Info "Please start Docker Desktop:"
    Write-Host "  1. Search 'Docker Desktop' in Start Menu"
    Write-Host "  2. Click to start Docker Desktop"
    Write-Host "  3. Wait for the whale icon in system tray to be steady"
    Write-Host "  4. Run this script again"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Check if Docker Compose is installed
Write-Host "Step 3: Checking Docker Compose..." -ForegroundColor White
$composeCmd = ""

# Try docker compose (v2 - plugin, included with Docker Desktop)
try {
    $composeVersion = docker compose version 2>$null
    if ($LASTEXITCODE -eq 0) {
        $composeCmd = "docker compose"
        Print-Success "Docker Compose v2 is installed: $composeVersion"
    } else {
        throw "Docker Compose v2 not found"
    }
} catch {
    # Try docker-compose (v1 - standalone)
    try {
        $composeVersion = docker-compose --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $composeCmd = "docker-compose"
            Print-Success "Docker Compose v1 is installed: $composeVersion"
        } else {
            throw "Docker Compose not found"
        }
    } catch {
        Print-Error "Docker Compose is not installed!"
        Write-Host ""
        Print-Info "Docker Compose should be included with Docker Desktop."
        Write-Host ""
        Write-Host "Please try:"
        Write-Host "  1. Restart Docker Desktop"
        Write-Host "  2. Update Docker Desktop to latest version"
        Write-Host ""
        Print-Info "For detailed instructions, see: WINDOWS.md"
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
}
Write-Host ""

# Check if model files exist
Write-Host "Step 4: Checking model files..." -ForegroundColor White
$modelPath1 = "backend\model\ConvNext_REAL-ESRGAN.pth"
$modelPath2 = "backend\model\REAL-ESRGAN.pth"

if ((Test-Path $modelPath1) -or (Test-Path $modelPath2)) {
    Print-Success "Model files found"
} else {
    Print-Warning "Model files not found in backend\model\"
    Write-Host ""
    Print-Info "Please download model files first:"
    Write-Host "  See: backend\model\README.md for download link"
    Write-Host ""
    $response = Read-Host "Continue without models? (y/N)"
    if ($response -notmatch '^[Yy]$') {
        Print-Info "Exiting. Please add model files and run again."
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
}
Write-Host ""

# Create necessary directories
Write-Host "Step 5: Creating directories..." -ForegroundColor White
New-Item -ItemType Directory -Force -Path "backend\data\uploads" | Out-Null
New-Item -ItemType Directory -Force -Path "backend\data\outputs" | Out-Null
Print-Success "Directories created"
Write-Host ""

# Build and start containers
Write-Host "Step 6: Building and starting Docker containers..." -ForegroundColor White
Write-Host ""
Print-Info "Running: $composeCmd up -d --build"
Write-Host ""

try {
    if ($composeCmd -eq "docker compose") {
        docker compose up -d --build
    } else {
        docker-compose up -d --build
    }

    if ($LASTEXITCODE -eq 0) {
        Print-Success "Docker containers started successfully!"
    } else {
        throw "Docker compose failed"
    }
} catch {
    Print-Error "Failed to start Docker containers"
    Write-Host ""
    Print-Info "Check logs with:"
    Write-Host "  $composeCmd logs -f"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Wait a moment for containers to start
Write-Host "Waiting for services to start..." -ForegroundColor White
Start-Sleep -Seconds 3
Write-Host ""

# Check container status
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Container Status" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
if ($composeCmd -eq "docker compose") {
    docker compose ps
} else {
    docker-compose ps
}
Write-Host ""

# Display access information
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  🎉 Application Started Successfully!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Print-Success "Frontend: http://localhost"
Print-Success "Backend API: http://localhost:8000"
Print-Success "API Docs: http://localhost:8000/docs"
Print-Success "Health Check: http://localhost:8000/api/health"
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Useful Commands" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "View logs:"
Write-Host "  $composeCmd logs -f" -ForegroundColor Yellow
Write-Host ""
Write-Host "Stop services:"
Write-Host "  $composeCmd down" -ForegroundColor Yellow
Write-Host ""
Write-Host "Restart services:"
Write-Host "  $composeCmd restart" -ForegroundColor Yellow
Write-Host ""
Write-Host "View running containers:"
Write-Host "  docker ps" -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Print-Info "Press any key to view logs, or close this window"
Write-Host ""

# Ask if user wants to view logs
$response = Read-Host "View logs now? (Y/n)"
if ($response -notmatch '^[Nn]$') {
    Write-Host ""
    Print-Info "Showing logs (Press Ctrl+C to exit)..."
    Write-Host ""
    if ($composeCmd -eq "docker compose") {
        docker compose logs -f
    } else {
        docker-compose logs -f
    }
}
