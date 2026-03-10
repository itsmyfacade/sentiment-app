"""
Tests for the Flask sentiment analysis API.

Covers:
- /health endpoint availability
- /analyze success path
- /analyze validation for missing text
"""

import os
import sys

import pytest

# Ensure the parent api/ directory is available on the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app


@pytest.fixture
def client():
    """
    Create a Flask test client for the application.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_ok(client):
    """
    /health should return HTTP 200 with the expected JSON payload.
    """
    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()
    assert data is not None
    assert data.get("status") == "ok"
    assert data.get("service") == "sentiment-api"
    assert "model_loaded" in data
    assert "model_name" in data


def test_analyze_success(client):
    """
    /analyze should return sentiment output for valid text input.
    """
    response = client.post(
        "/analyze",
        json={"text": "I absolutely love this product!"}
    )

    assert response.status_code == 200

    data = response.get_json()
    assert data is not None
    assert "label" in data
    assert "score" in data
    assert "inference_time_ms" in data
    assert data["label"] in {"POSITIVE", "NEGATIVE"}
    assert isinstance(data["score"], float)
    assert isinstance(data["inference_time_ms"], float)


def test_analyze_missing_text(client):
    """
    /analyze should return HTTP 400 when text is missing.
    """
    response = client.post("/analyze", json={})

    assert response.status_code == 400

    data = response.get_json()
    assert data is not None
    assert data.get("error") == "text is required"