#!/bin/bash

# Start Streamlit Frontend
echo "🎨 Starting Investment Analyst AI Frontend..."

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment
cd "$PROJECT_ROOT"
source venv/bin/activate

# Navigate to frontend directory
cd frontend

# Start Streamlit
echo "Frontend will be available at: http://localhost:8501"
echo ""

python -m streamlit run app.py --server.port 8501
