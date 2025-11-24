#!/bin/bash
echo "=== Checking Backend Status ==="
echo ""

# Check if backend container is running
echo "1. Container status:"
docker-compose ps backend
echo ""

# Check backend logs
echo "2. Recent backend logs (last 50 lines):"
docker-compose logs --tail=50 backend
echo ""

# Try to reach backend health endpoint
echo "3. Testing backend health endpoint:"
curl -v http://localhost:8000/api/health 2>&1 | grep -E "HTTP|Connected|failed"
echo ""

# Check if backend is listening on port 8000
echo "4. Port 8000 status:"
netstat -tlnp 2>/dev/null | grep 8000 || ss -tlnp 2>/dev/null | grep 8000 || echo "Command not available, skipping"
