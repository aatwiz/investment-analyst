"""
Backend API tests
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "Investment Analyst" in data["message"]


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_file_list_endpoint():
    """Test file listing endpoint"""
    response = client.get("/api/v1/files/list")
    assert response.status_code == 200
    data = response.json()
    assert "files" in data
    assert "count" in data
