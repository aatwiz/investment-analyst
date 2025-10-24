"""
Pytest configuration and fixtures
"""
import pytest
import os
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Set test environment variables
os.environ["TESTING"] = "True"
os.environ["UPLOAD_DIR"] = "./tests/test_uploads"
os.environ["PROCESSED_DIR"] = "./tests/test_processed"


@pytest.fixture
def test_upload_dir(tmp_path):
    """Create temporary upload directory for testing"""
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    return upload_dir


@pytest.fixture
def sample_file(tmp_path):
    """Create a sample test file"""
    file_path = tmp_path / "test.txt"
    file_path.write_text("This is a test file")
    return file_path
