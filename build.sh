#!/bin/bash
set -e

SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR"

echo "Starting EchoVault Build Cycle..."

# Backend
echo "Building Backend..."
cd backend
if [ ! -d "venv" ]; then
    uv venv
fi
source venv/bin/activate
uv pip install -r requirements.txt
cd ..

# Frontend
echo "Building Frontend..."
cd frontend
npm install
npm run build
cd ..

echo "Build Cycle Complete!"
