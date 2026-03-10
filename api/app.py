"""
Sentiment Analysis API using Flask.

This API uses a Hugging Face model (DistilBERT SST-2)
to predict if text is positive or negative.

Endpoints:
- GET /health -> quick check if the API is running
- POST /analyze -> takes JSON {"text": "..."} and returns sentiment + score
"""

import logging
import os
import time
from typing import Any, Dict

from flask import Flask, jsonify, request
from flask_cors import CORS
from transformers import pipeline

# -----------------------------------------------------------------------------
# App setup
# -----------------------------------------------------------------------------
app = Flask(__name__)

# allow all origins for this project
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "distilbert-base-uncased-finetuned-sst-2-english",
)
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8001"))
DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Lazy-loaded model
# -----------------------------------------------------------------------------
_sentiment = None


def get_sentiment():
    """
    Load the sentiment pipeline once and reuse it for all future requests.
    """
    global _sentiment
    if _sentiment is None:
        logger.info("Loading sentiment model: %s", MODEL_NAME)
        _sentiment = pipeline(
            task="sentiment-analysis",
            model=MODEL_NAME,
        )
        logger.info("Sentiment model loaded successfully")
    return _sentiment


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def error_response(message: str, status_code: int) -> tuple:
    return jsonify({"error": message}), status_code


def success_response(payload: Dict[str, Any], status_code: int = 200) -> tuple:
    return jsonify(payload), status_code


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.get("/health")
def health():
    """
    Simple health check endpoint.
    Does not force model inference.
    """
    return success_response(
        {
            "status": "ok",
            "service": "sentiment-api",
            "model_loaded": _sentiment is not None,
            "model_name": MODEL_NAME,
        }
    )


@app.get("/")
def index():
    """
    Simple landing route so hitting the root URL does not 404.
    """
    return success_response(
        {
            "service": "sentiment-api",
            "model_name": MODEL_NAME,
            "endpoints": {
                "health": "GET /health",
                "analyze": 'POST /analyze (body: {"text": "..."})',
            },
        }
    )


@app.get("/favicon.ico")
def favicon():
    """
    Browsers often request /favicon.ico automatically.
    Return 204 to avoid noisy 404 logs.
    """
    return ("", 204)


@app.route("/analyze", methods=["OPTIONS"])
def analyze_options():
    """
    Respond to browser preflight requests.
    """
    return ("", 204)


@app.post("/analyze")
def analyze():
    """
    Main endpoint that does the sentiment analysis.

    Expects:
        {"text": "I love this product!"}

    Returns:
        {
            "label": "POSITIVE",
            "score": 0.998,
            "inference_time_ms": 123.45
        }
    """
    try:
        data = request.get_json(silent=True) or {}
        text = str(data.get("text") or "").strip()

        if not text:
            return error_response("text is required", 400)

        if len(text) > 5000:
            return error_response("text is too long", 400)

        sentiment_pipeline = get_sentiment()

        start_time = time.perf_counter()
        result = sentiment_pipeline(text)[0]
        end_time = time.perf_counter()

        inference_time_ms = round((end_time - start_time) * 1000, 2)

        response = {
            "label": result["label"],
            "score": round(float(result["score"]), 6),
            "inference_time_ms": inference_time_ms,
        }

        logger.info(
            "Prediction completed | label=%s | score=%.6f | inference_time_ms=%.2f",
            response["label"],
            response["score"],
            response["inference_time_ms"],
        )

        return success_response(response)

    except Exception:
        logger.exception("Unexpected error during /analyze")
        return error_response("internal server error", 500)


# -----------------------------------------------------------------------------
# Response headers
# -----------------------------------------------------------------------------
@app.after_request
def add_cors_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp


# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("Starting sentiment-api on %s:%s", HOST, PORT)
    app.run(host=HOST, port=PORT, debug=DEBUG)