"""
Basic test file for the Flask API.

This just checks that the /health endpoint is working.
It should return status code 200 and the expected JSON keys.
"""

import json
from app import app  # import the Flask app from app.py

def test_health_ok():
    # create a test client (lets us call the app without running the server)
    client = app.test_client()

    # call the /health endpoint
    resp = client.get("/health")

    # check that the server responded with a success code
    assert resp.status_code == 200

    # parse the JSON response
    data = json.loads(resp.data)

    # make sure the expected keys are there
    assert data.get("status") == "ok"
    assert data.get("service") == "sentiment-api"