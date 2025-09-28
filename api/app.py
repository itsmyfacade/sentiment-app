"""
Sentiment Analysis API using Flask.

This small API uses a Hugging Face model (DistilBERT SST-2)
to predict if text is positive or negative.

Endpoints:
- GET /health -> quick check if the API is running
- POST /analyze -> takes JSON {"text": "..."} and returns sentiment + score
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline

# create the Flask app
app = Flask(__name__)

# allow all origins for this demo; tighten later if needed
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

# lazy-load the model on first use so the server can start immediately
_sentiment = None
def get_sentiment():
    global _sentiment
    if _sentiment is None:
        _sentiment = pipeline(
            task="sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
    return _sentiment

@app.get("/health")
def health():
    """
    Simple health check endpoint.
    Used by us (or Render) to make sure the service is alive.
    Does not run the model, just returns a JSON message.
    """
    return jsonify({"status": "ok", "service": "sentiment-api"}), 200

@app.post("/analyze")
def analyze():
    """
    Main endpoint that does the sentiment analysis.

    Expects a JSON body like: {"text": "I love this product!"}
    Returns something like:
        {"label": "POSITIVE", "score": 0.998}
    """
    # read the request body
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()

    # if text is missing, return error
    if not text:
        return jsonify({"error": "text is required"}), 400

    # run the model on the input text
    result = get_sentiment()(text)[0]

    # return the label (POSITIVE/NEGATIVE) and the confidence score
    return jsonify({
        "label": result["label"],
        "score": float(result["score"])
    }), 200

@app.get("/")
def index():
    """
    Simple landing route so hitting the root URL doesn't 404.
    Shows the available endpoints for quick reference.
    """
    return jsonify({
        "service": "sentiment-api",
        "endpoints": {
            "health": "/health",
            "analyze": "POST /analyze  (body: {\"text\": \"...\"})"
        }
    }), 200


@app.get("/favicon.ico")
def favicon():
    """
    Browsers often request /favicon.ico automatically.
    We don't serve an icon here, so just return 204 (no content)
    to avoid noisy 404 logs.
    """
    return ("", 204)

@app.after_request
def add_cors_headers(resp):
    # standard CORS headers so browser preflight succeeds
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp

# respond to preflight OPTIONS for /analyze
@app.route("/analyze", methods=["OPTIONS"])
def analyze_options():
    return ("", 204)

# run locally with: python app.py
# in production we will use gunicorn instead of this
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)