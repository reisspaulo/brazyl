"""
Configuração de fixtures do pytest.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Client de teste do FastAPI."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_api_key():
    """API Key para testes."""
    return "test-api-key-12345"

