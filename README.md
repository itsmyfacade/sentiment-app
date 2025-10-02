
# Sentiment Analysis App

A small Flask API that classifies text as **positive** or **negative** using a Hugging Face model.  
Built for learning and demo purposes.

Note: I originally built this project a few months ago. This version is an **expanded rebuild** with a cleaner setup (Flask API + Next.js frontend) so I could practice structuring a full-stack app again.

---

## Features
- `GET /health` → quick check if the API is running  
- `POST /analyze` → send text and get back a sentiment label + confidence score  

---

## Local Setup (Windows PowerShell)

Clone the repo and go into the folder:

```powershell
git clone https://github.com/itsmyfacade/sentiment-app.git
cd sentiment-app
```

**API (backend)**

Create and activate a virtual environment:
```powershell
cd api
python -m venv .venv
.\.venv\Scripts\Activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the API:

```powershell
python app.py
```

The backend will start on:
👉 http://127.0.0.1:8001

---

**Web (frontend)**

Open a new terminal, go to the web folder:

```powershell
cd web
npm install
npm run dev
```

The frontend will start on:
👉 http://127.0.0.1:3000

---

## Example Requests

**Health check:**

```powershell
curl http://127.0.0.1:8001/health
```

**Analyze (classify sentiment):**

```powershell
curl -X POST http://127.0.0.1:8001/analyze ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"I absolutely love this product!\"}"
```

Or just open the frontend at http://127.0.0.1:3000 and use the form.

---

## Testing

Run quick tests with pytest:

```powershell
cd api
python -m pytest -q
```

---

## Notes
	•	Model is distilbert-base-uncased-finetuned-sst-2-english from Hugging Face.
	•	Frontend is Next.js 14 with a simple form + proxy route.
	•	Project started as backend-only, later expanded into a full-stack demo.

---

