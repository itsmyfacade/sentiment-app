# Sentiment Analysis Service

**Live frontend:** https://sentiment-lab-web.onrender.com
**Live API:** https://sentiment-lab-api.onrender.com

Production-oriented sentiment classification API powered by a transformer model. Designed as a modular machine learning inference service with a separate frontend client.

## Overview

This project implements a REST-based sentiment classification service using a pre-trained DistilBERT model. The system exposes inference endpoints through a Flask API and serves predictions to a Next.js frontend.

The architecture emphasizes:

- Clean separation of backend and frontend
- Reusable inference pipeline
- Testable API endpoints
- Production-aware structure

## Project History

This project was originally built in October 2025 as an early sentiment analysis application.
The current version is a production-focused rebuild with improved API structure, automated tests, inference timing, Docker support, and deployment-oriented documentation.

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

## Security and deployment boundary

Set `FRONTEND_ORIGINS` to the exact frontend origin before exposing the API. The API applies bounded request sizes, a single in-process inference slot, a small per-process fixed-window request limit, and safe public errors. These controls are suitable for a controlled demonstration, not a substitute for a distributed production rate limiter or authentication. The test suite mocks transformer inference, so running tests does not download the model. A real demo still requires the Hugging Face model download and sufficient memory for PyTorch. The public deployment is a separate Render configuration; this repository does not claim production uptime or distributed load-test coverage.
## Final frontend experience

The Next.js client is a dark, keyboard-friendly analysis workspace with a 5,000-character input limit, example prompts, live character count, disabled duplicate submissions, model-loading feedback, actual score and inference-time presentation, and explicit binary-classification limitations.

```text
Browser → Next.js /api/analyze proxy → Flask /analyze → DistilBERT SST-2
```

Use Python 3.12 for the documented local environment. The Dockerfile installs CPU-only Torch; isolated container build and real inference verification have passed. The deployed API has passed live health and positive/negative inference checks on Render Free, and the public frontend plus its `/api/analyze` proxy have returned live application responses.
## Verified two-terminal startup

```powershell
# Terminal 1 - backend
cd api
py -3.12 -m venv .venv312
.\.venv312\Scripts\Activate.ps1
$env:PORT = "8011"
$env:FRONTEND_ORIGINS = "http://localhost:3111"
pip install -r requirements.txt
python app.py

# Terminal 2 - frontend
cd web
npm ci
$env:API_URL = "http://127.0.0.1:8011"
npm run dev -- --port 3111
```

Open `http://localhost:3111`. The backend health endpoint is `http://127.0.0.1:8011/health`.

The workbench also supports bounded batch analysis of up to 10 entries, session-only history, aggregate positive/negative distribution, and CSV export. Submitted text is not persisted by the frontend. The server-side proxy allows up to three minutes for a sleeping backend to cold-start, then returns a safe error instead of leaving the UI waiting indefinitely.

## Container and deployment boundary

The backend Dockerfile uses one Gunicorn `gthread` worker with two threads, CPU-only PyTorch, the Render `PORT` contract, and lazy DistilBERT initialization. The single process preserves model memory while allowing the lightweight `/health` endpoint to respond during inference. A Render deployment should use separate frontend and backend services, configure the frontend `API_URL` with the private backend service URL, and retain deployment-level abuse protection.

## Final acceptance measurements

- Isolated Docker build: passed.
- Isolated real inference: passed with DistilBERT returning `POSITIVE` for the acceptance input.
- Strict 512 MiB container memory observed: approximately 405 MiB during cold-started real inference.
- Image size observed: approximately 1.66 GB.
- QA containers used dedicated names, ports, and network; no MAATMARK resources were modified.

## Render preparation

`render.yaml` defines a free Docker API service and a free Node frontend service. Set `FRONTEND_ORIGINS` on the API to the final frontend URL and `API_URL` on the frontend to the API URL during Blueprint setup. The service binds Render's `PORT` and health checks `/health`. The strict 512 MiB local acceptance run completed real inference at approximately 405 MiB, leaving limited headroom; cold starts, free-hour suspension, and public abuse protection still require deployment-specific validation.

## Verified live API

- API: https://sentiment-lab-api.onrender.com
- `GET /health`: verified HTTP 200.
- `POST /analyze`: verified positive and negative DistilBERT responses.

The public frontend and API are deployed as separate Render Free services. Cold starts can take longer than warm requests, and free services may suspend when free-instance limits are exhausted.

## GitHub Actions CI

The repository workflow runs on pushes to `main`, pull requests targeting `main`, and manual dispatch. It runs mocked Python API tests, Python syntax checks, Render Blueprint validation, TypeScript validation, a Next.js production build, and `npm audit --audit-level=high`. Ordinary CI does not download the DistilBERT model; real-model validation is performed separately through Docker and the deployed service.
