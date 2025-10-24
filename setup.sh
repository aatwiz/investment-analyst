#!/bin/bash

# Investment Analyst AI Agent - Setup Script
# This script sets up the complete development environment

set -e  # Exit on error

echo "🚀 Setting up Investment Analyst AI Agent..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -r requirements.txt

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env file and add your API keys${NC}"
else
    echo -e "${YELLOW}.env file already exists${NC}"
fi

# Create necessary directories
echo -e "${BLUE}Creating data directories...${NC}"
mkdir -p data/uploads data/processed data/outputs logs models

echo -e "${GREEN}✓ Directories created${NC}"

# Install playwright browsers (for web scraping)
echo -e "${BLUE}Installing Playwright browsers (optional, press Ctrl+C to skip)...${NC}"
read -p "Install Playwright browsers? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    playwright install chromium
    echo -e "${GREEN}✓ Playwright browsers installed${NC}"
fi

echo ""
echo -e "${GREEN}✅ Setup completed successfully!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Edit .env file and add your API keys"
echo "2. Start the backend: cd backend && uvicorn main:app --reload"
echo "3. Start the frontend: streamlit run frontend/app.py"
echo ""
echo -e "${BLUE}Or use the quick start commands:${NC}"
echo "  ./scripts/start_backend.sh   - Start FastAPI backend"
echo "  ./scripts/start_frontend.sh  - Start Streamlit frontend"
echo ""
