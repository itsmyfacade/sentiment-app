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
import app as app_module


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


def test_analyze_success(client, monkeypatch):
    """
    /analyze should return sentiment output for valid text input.
    """
    monkeypatch.setattr(app_module, "get_sentiment", lambda: lambda _text: [{"label": "POSITIVE", "score": 0.999885}])
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


def test_analyze_rejects_non_string_text(client):
    response = client.post("/analyze", json={"text": 123})
    assert response.status_code == 400
    assert response.get_json()["error"] == "text must be a string"


def test_analyze_rejects_oversized_text(client):
    response = client.post("/analyze", json={"text": "x" * 5001})
    assert response.status_code == 400
    assert response.get_json()["error"] == "text is too long"


def test_analyze_rejects_malformed_json(client):
    response = client.post("/analyze", data="{", content_type="application/json")
    assert response.status_code == 400
    assert response.get_json()["error"] == "request body must be a JSON object"


def test_analyze_model_failure_is_safe(client, monkeypatch):
    def fail_model():
        raise RuntimeError("model details must not reach the client")

    monkeypatch.setattr(app_module, "get_sentiment", fail_model)
    response = client.post("/analyze", json={"text": "hello"})
    assert response.status_code == 500
    assert response.get_json() == {"error": "internal server error"}


def test_analyze_uses_mocked_model(client, monkeypatch):
    monkeypatch.setattr(app_module, "get_sentiment", lambda: lambda _text: [{"label": "POSITIVE", "score": 0.875}])
    response = client.post("/analyze", json={"text": "This works."})
    assert response.status_code == 200
    assert response.get_json()["label"] == "POSITIVE"
