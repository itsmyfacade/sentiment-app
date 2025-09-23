# Sentiment Analysis App

This is a simple sentiment analysis API built with **Flask** and **Hugging Face Transformers**.  
It uses the DistilBERT SST-2 model to classify text as **positive** or **negative**.

I built this project to practice combining a machine learning model with a backend API, and to make it easy to deploy online.

---

## Features
- `GET /health` → returns a JSON response to confirm the service is running
- `POST /analyze` → takes `{"text": "..."}` and returns sentiment label + confidence score
- CORS enabled so a frontend app can call the API

---

## Local Setup

Clone the repo and create a virtual environment:

```bash
git clone https://github.com/itsmyfacade/sentiment-app.git
cd sentiment-app
python -m venv .venv
.\.venv\Scripts\activate   # (Windows)
pip install -r api/requirements.txt

Run the backend:

cd api
python app.py

The service will be available at:
👉 http://localhost:8001

---

Example Requests

Health check:

curl http://localhost:8001/health

Analyze text:

curl -X POST http://localhost:8001/analyze ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"I absolutely love this product!\"}"


---

Testing

Run unit tests with pytest:

cd api
python -m pytest -q


---

Deployment (Render)

This app can be deployed for free on Render.

Backend Service Settings:
	•	Root Directory: api
	•	Build Command:

pip install -r requirements.txt


	•	Start Command:

gunicorn -w 1 -k gthread -b 0.0.0.0:10000 app:app


	•	Health Check Path: /health
