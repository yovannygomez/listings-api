import pytest
from fastapi.testclient import TestClient

from app.main import app, seed


@pytest.fixture
def client():
    seed()
    return TestClient(app)
