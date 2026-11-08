# PhishGuard — Hybrid ML + Rules Cloud Mini Project

React + FastAPI + scikit-learn project for a two-member college lab team. Primary beginner-friendly deployment: **Vercel frontend + Render backend**. Optional AWS architecture is documented below and in `docs/REPORT.md`.

## What is implemented?
- React scanner for messages/SMS and URLs.
- Python rule engine for urgency, credential requests, account threats, links, shorteners, and URL structure.
- TF-IDF + Logistic Regression classifier trained from small synthetic examples at API startup.
- Hybrid score: 65% rule score + 35% ML probability.
- Recent scan history in backend memory (clears on restart; not persistent).
- FastAPI `/analyze`, `/history`, `/health` endpoints.
- Automated backend tests.

## Requirements
- Node.js 20+ and npm
- Python 3.11
- GitHub account (recommended for cloud deployment)

## A. Run locally on Windows / VS Code
Open the project root in VS Code.

### Backend terminal
```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
uvicorn app:app --reload --port 8000
```
If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again. Alternatively run `.venv\Scripts\python.exe -m pip install -r requirements-dev.txt` and `.venv\Scripts\python.exe -m uvicorn app:app --reload --port 8000` without activating.

API docs: http://127.0.0.1:8000/docs
Health check: http://127.0.0.1:8000/health

### Frontend in a second terminal
```powershell
cd frontend
npm install
```
Create `frontend/.env` with:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```
Then start it:
```powershell
npm run dev
```
Open the localhost URL printed by Vite. Restart Vite if `.env` changes.

For offline UI-only demo, leave `VITE_API_BASE_URL` unset. The frontend will use a simplified local demo; ML results only come from the backend API.

## B. Run tests
With the backend virtual environment active:
```powershell
cd backend
python -m pytest -q
```

## C. Deploy backend to Render (free plan availability may change)
1. Create a GitHub repository and upload the contents of this project. Do not upload `.env` files or credentials.
2. In Render, create a **New Web Service** and connect the repository.
3. Set **Root Directory** to `backend`.
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
6. Add environment variable `FRONTEND_ORIGIN` after frontend deployment; initially it may be `*` for testing only.
7. Deploy. Open `https://YOUR-SERVICE.onrender.com/health`; expect `{"status":"healthy"}`.
8. Free services may sleep and cold-start. In-memory history clears when the process restarts.

A `render.yaml` blueprint is also included, but you may create the service manually if the dashboard setup is easier.

## D. Deploy React frontend to Vercel
1. Import the same GitHub repository into Vercel.
2. Set **Root Directory** to `frontend`.
3. Framework preset: Vite. Build command `npm run build`; output directory `dist`.
4. Add environment variable `VITE_API_BASE_URL=https://YOUR-SERVICE.onrender.com` (your actual Render URL, no trailing slash).
5. Deploy and test a sample message.
6. Update the Render environment variable `FRONTEND_ORIGIN` to your exact Vercel origin, e.g. `https://your-project.vercel.app`, then redeploy/restart the API if required.

CORS is not authentication. Keep synthetic messages only.

## E. AWS configuration (optional extension)
The primary backend uses scikit-learn on Render. Do not point it at an AWS API Gateway URL unless you have deployed a compatible AWS implementation. For an AWS version, use API Gateway + Lambda + DynamoDB and port the hybrid logic into a Lambda-compatible package/container, or expose the FastAPI app via a container service. The earlier simple Lambda template from a rule-only version is not the same hybrid ML backend.

If your instructor requires the listed AWS services, a clean extension is:
- S3/CloudFront: host the built React files (CloudFront is preferable for HTTPS/private bucket origin).
- API Gateway: HTTPS endpoint.
- Lambda: Python request handler and hybrid detector, packaged with compatible scikit-learn dependencies or a container image.
- DynamoDB: persistent scan history.
- IAM: Lambda role limited to the one table's required actions.
- CORS: allow only the deployed frontend origin.

AWS setup checklist: choose a region; create a DynamoDB table with partition key `id` (String); create a Lambda execution role with CloudWatch Logs permissions and least-privilege DynamoDB `PutItem`/`Query` or `Scan` access to that table; deploy the backend package/container; create API Gateway routes `POST /analyze`, `GET /history`, and `GET /health`; configure CORS; deploy a stage; set `VITE_API_BASE_URL` to that API URL and rebuild/redeploy the frontend. A model file or dependencies must be included in the Lambda deployment artifact; installing scikit-learn at runtime is not recommended.

This repo does not automatically provision the hybrid AWS version. Use Render + Vercel for the working primary deployment unless your lecturer specifically requires AWS resources.

## Costs and safety
- Check current Render/Vercel plan availability and quotas before deploying; free terms can change.
- AWS services may charge even if a free tier is available. Set a budget alert and delete resources after the demo.
- Never scan confidential messages. This is a teaching prototype, not antivirus or a reputation service. It does not open URLs.
- The synthetic dataset is tiny and not suitable for real-world accuracy claims. Rule/ML score is an estimate, not calibrated risk probability.
