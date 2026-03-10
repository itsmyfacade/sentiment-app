# Sentiment Analysis Service

Production-oriented sentiment classification API powered by a transformer model. Designed as a modular machine learning inference service with a separate frontend client.

## Overview

This project implements a REST-based sentiment classification service using a pre-trained DistilBERT model. The system exposes inference endpoints through a Flask API and serves predictions to a Next.js frontend.

The architecture emphasizes:

- Clean separation of backend and frontend
- Reusable inference pipeline
- Testable API endpoints
- Production-aware structure

## Model

- Model: `distilbert-base-uncased-finetuned-sst-2-english`
- Framework: Hugging Face Transformers with PyTorch
- Task: Binary sentiment classification
- Output: Label and confidence score

The model is initialized once and reused across inference requests to minimize repeated load overhead.

## API Endpoints

### Health Check

`GET /health`

Returns service status and model metadata.

### Sentiment Analysis

`POST /analyze`

Request:

```json
{
  "text": "I absolutely love this product!"
}
```

Response:

```json
{
  "label": "POSITIVE",
  "score": 0.999885,
  "inference_time_ms": 37.81
}
```

## Architecture

```
sentiment-app/
|-- api/
|   |-- app.py
|   |-- requirements.txt
|   |-- tests/
|-- web/
|   |-- app/
|-- README.md
```

- Backend handles model inference and API routing
- Frontend provides the client interaction layer
- Service boundaries support independent deployment

## Design Principles

- Separation of concerns between inference service and UI
- Stateless API design
- Deterministic JSON responses
- Easily containerizable backend
- Model abstraction for future swap/upgrade

## Local Setup

### Clone the Repository

```powershell
git clone https://github.com/itsmyfacade/sentiment-app.git
cd sentiment-app
```

### Backend

```powershell
cd api
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
python app.py
```

Backend runs on:

`http://127.0.0.1:8001`

### Frontend

```powershell
cd web
npm install
npm run dev
```

Frontend runs on:

`http://127.0.0.1:3000`

## Example Requests

### Health Check

```bash
curl http://127.0.0.1:8001/health
```

Example response:

```json
{
  "model_loaded": false,
  "model_name": "distilbert-base-uncased-finetuned-sst-2-english",
  "service": "sentiment-api",
  "status": "ok"
}
```

### Analyze Sentiment

```bash
curl -X POST "http://127.0.0.1:8001/analyze"   -H "Content-Type: application/json"   -d '{"text":"I absolutely love this product!"}'
```

Example response:

```json
{
  "inference_time_ms": 37.81,
  "label": "POSITIVE",
  "score": 0.999885
}
```

You can also open the frontend at `http://127.0.0.1:3000` and submit text through the form.

## Docker

The backend service can be containerized and deployed using Docker.
The container runs the Flask API using Gunicorn for production-style serving.

### Build the Image

From the `api` directory:

```bash
docker build -t sentiment-api .
```

### Run the Container

```bash
docker run -p 8001:8001 sentiment-api
```

The API will be available at:

`http://127.0.0.1:8001`

### Verify the Service

Health check:

```bash
curl http://127.0.0.1:8001/health
```

Sentiment inference:

```bash
curl -X POST "http://127.0.0.1:8001/analyze"   -H "Content-Type: application/json"   -d '{"text":"I absolutely love this product!"}'
```

### Notes

- Gunicorn is used as the production WSGI server inside the container.
- The model is initialized once and reused across requests.
- The first inference request may take longer due to model initialization.

## Testing

Run the backend tests with:

```powershell
cd api
pytest -q
```

Current test coverage includes:

- `/health` endpoint validation
- `/analyze` success path
- `/analyze` missing input validation

## Performance

Local CPU benchmark using a warm model:

- Native local inference observed around `16 ms`
- Containerized inference observed around `38 ms`
- Model is reused across requests to avoid reload overhead
- Response includes label, confidence score, and latency measurement

## Production Considerations

- Model initialized once and reused across requests
- Structured JSON responses
- Input validation for missing and oversized text
- REST interface suitable for containerization
- Test coverage for critical endpoints
- Environment variable support for model name and runtime configuration

## Tech Stack

- Python
- Flask
- PyTorch
- Hugging Face Transformers
- Next.js
- TypeScript