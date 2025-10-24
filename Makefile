.PHONY: help setup install start start-backend start-frontend stop test clean

help:
	@echo "Investment Analyst AI Agent - Available Commands"
	@echo ""
	@echo "  make setup          - Initial project setup"
	@echo "  make install        - Install dependencies"
	@echo "  make start          - Start both backend and frontend"
	@echo "  make start-backend  - Start backend only"
	@echo "  make start-frontend - Start frontend only"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Clean temporary files"
	@echo "  make format         - Format code with black"
	@echo "  make lint           - Lint code with flake8"
	@echo ""

setup:
	@echo "Setting up project..."
	@chmod +x setup.sh scripts/*.sh
	@./setup.sh

install:
	@echo "Installing dependencies..."
	@pip install -r requirements.txt

start:
	@echo "Starting Investment Analyst AI Agent..."
	@./scripts/start_all.sh

start-backend:
	@echo "Starting backend..."
	@./scripts/start_backend.sh

start-frontend:
	@echo "Starting frontend..."
	@./scripts/start_frontend.sh

test:
	@echo "Running tests..."
	@pytest tests/ -v

test-cov:
	@echo "Running tests with coverage..."
	@pytest tests/ --cov=backend --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

clean:
	@echo "Cleaning temporary files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf htmlcov/ .coverage 2>/dev/null || true
	@echo "Clean complete!"

format:
	@echo "Formatting code..."
	@pip install black isort
	@black backend/ frontend/ tests/
	@isort backend/ frontend/ tests/
	@echo "Code formatted!"

lint:
	@echo "Linting code..."
	@pip install flake8
	@flake8 backend/ frontend/ tests/ --max-line-length=100
	@echo "Linting complete!"

docs:
	@echo "Opening documentation..."
	@open README.md

api-docs:
	@echo "API documentation available at:"
	@echo "http://localhost:8000/api/docs"

env:
	@echo "Creating .env file from template..."
	@cp .env.example .env
	@echo ".env file created. Please edit and add your API keys."

requirements:
	@echo "Generating requirements.txt..."
	@pip freeze > requirements.txt
	@echo "requirements.txt updated!"
