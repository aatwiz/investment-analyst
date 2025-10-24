#!/bin/bash

# Start both Backend and Frontend
echo "🚀 Starting Investment Analyst AI Agent (Full Stack)..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Activate virtual environment
echo "Activating virtual environment..."
cd "$PROJECT_ROOT"
source venv/bin/activate

# Set PYTHONPATH
export PYTHONPATH="${PROJECT_ROOT}/backend:${PYTHONPATH}"

# Start backend in background
echo "Starting Backend..."
cd "$PROJECT_ROOT/backend"
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend in background
echo "Starting Frontend..."
cd "$PROJECT_ROOT/frontend"
python -m streamlit run app.py --server.port 8501 &
FRONTEND_PID=$!

echo ""
echo "✅ Services started!"
echo "📊 Frontend: http://localhost:8501"
echo "🔧 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/api/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for processes
wait
