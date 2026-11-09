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
import threading
import time
from typing import Any, Dict

from flask import Flask, jsonify, request
from flask_cors import CORS

# -----------------------------------------------------------------------------
# App setup
# -----------------------------------------------------------------------------
app = Flask(__name__)

# allow all origins for this project
TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv("FRONTEND_ORIGINS", "http://localhost:3000").split(",") if origin.strip()]
CORS(app, resources={r"/*": {"origins": TRUSTED_ORIGINS}}, supports_credentials=False)

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
app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", "20000"))
INFERENCE_CONCURRENCY = max(1, int(os.getenv("INFERENCE_CONCURRENCY", "1")))
RATE_LIMIT_REQUESTS = max(1, int(os.getenv("RATE_LIMIT_REQUESTS", "30")))
RATE_LIMIT_WINDOW_SECONDS = max(1, int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")))

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
_inference_slots = threading.BoundedSemaphore(INFERENCE_CONCURRENCY)
_rate_limit_lock = threading.Lock()
_rate_limit_state: dict[str, tuple[float, int]] = {}


def get_sentiment():
    """
    Load the sentiment pipeline once and reuse it for all future requests.
    """
    global _sentiment
    if _sentiment is None:
        from transformers import pipeline

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


def request_is_rate_limited() -> bool:
    """Apply a small per-process fixed-window limit for public demo protection."""
    now = time.monotonic()
    client_key = request.remote_addr or "unknown"
    with _rate_limit_lock:
        window_start, count = _rate_limit_state.get(client_key, (now, 0))
        if now - window_start >= RATE_LIMIT_WINDOW_SECONDS:
            window_start, count = now, 0
        if count >= RATE_LIMIT_REQUESTS:
            _rate_limit_state[client_key] = (window_start, count)
            return True
        _rate_limit_state[client_key] = (window_start, count + 1)
    return False


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
        if request_is_rate_limited():
            return error_response("request rate limit exceeded", 429)
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return error_response("request body must be a JSON object", 400)

        raw_text = data.get("text")
        if "text" not in data:
            return error_response("text is required", 400)
        if not isinstance(raw_text, str):
            return error_response("text must be a string", 400)
        text = raw_text.strip()

        if not text:
            return error_response("text is required", 400)

        if len(text) > 5000:
            return error_response("text is too long", 400)

        if not _inference_slots.acquire(blocking=False):
            return error_response("inference service is busy; retry shortly", 429)

        try:
            sentiment_pipeline = get_sentiment()
            start_time = time.perf_counter()
            result = sentiment_pipeline(text)[0]
            end_time = time.perf_counter()
        finally:
            _inference_slots.release()

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


@app.errorhandler(413)
def request_too_large(_error):
    return error_response("request body is too large", 413)


# -----------------------------------------------------------------------------
# Response headers
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("Starting sentiment-api on %s:%s", HOST, PORT)
    app.run(host=HOST, port=PORT, debug=DEBUG)
