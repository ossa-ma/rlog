#!/bin/bash
# Quick start script for rlog API

set -e

echo "Starting rlog API..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your GitHub OAuth credentials"
    exit 1
fi

# Sync dependencies with uv
echo "Syncing dependencies..."
uv sync

# Run the API
echo "Starting server at http://localhost:8000"
echo "API docs at http://localhost:8000/docs"
echo ""
uv run uvicorn main:app --reload
