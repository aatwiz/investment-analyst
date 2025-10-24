#!/bin/bash

# Start FastAPI Backend
echo "🚀 Starting Investment Analyst AI Backend..."

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment
cd "$PROJECT_ROOT"
source venv/bin/activate

# Navigate to backend directory
cd backend

# Start backend with uvicorn
echo "Backend will be available at: http://localhost:8000"
echo "API docs at: http://localhost:8000/api/docs"
echo ""

# Set PYTHONPATH to include backend directory
export PYTHONPATH="${PROJECT_ROOT}/backend:${PYTHONPATH}"

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
