# HealthSphere AI — Full-Stack Capstone Project

An AI-assisted, multi-disease clinical decision-support platform with a real React frontend
and a real FastAPI backend. Patients log vitals/upload lab reports, get an explainable
multi-disease risk score, and are supported by a Patient Care Agent; doctors get a
prioritized worklist from a Clinician Assist Agent, draft care plans with medicine
decision-support, and review/approve everything. A RAG chatbot handles FAQs and general
health questions, escalating to a human whenever it should.

## Stack
- **Backend:** Python, FastAPI, SQLAlchemy, SQLite (swappable to Postgres), JWT auth
- **Frontend:** React 19, Vite, Tailwind CSS, React Router, Axios, **Three.js** (landing hero),
  **GSAP** (scroll/entrance animations), Recharts (health timeline charts), lucide-react (icons)
- **AI layer:** Patient Care Agent, Clinician Assist Agent, RAG chatbot (ChromaDB + Anthropic
  Claude), medicine decision-support (RxNav/RxNorm + openFDA)
- **Infra:** Docker Compose (Postgres, Redis, ChromaDB, backend, agent-worker, frontend)

---

## Quick start (local dev, no Docker)

### 1. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate.bat        # Windows
# source venv/bin/activate       # macOS/Linux

pip install -r requirements.txt
copy .env.example .env           # Windows: copy | macOS/Linux: cp
# Edit .env and add your ANTHROPIC_API_KEY (only needed for the RAG chatbot's generation step)

# Run the API (auto-creates all tables in db/healthsphere.db on startup)
uvicorn app.main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

The included `db/healthsphere.db` already has the full schema (12 tables: users,
patient_profiles, vitals_records, lab_reports, assessment_results, care_plans,
notifications, agent_tasks, chat_sessions, chat_messages, escalation_tickets,
medicine_recommendations) — you can start from it or delete it to start fresh
(it will be recreated automatically).

### 2. Frontend
```bash
cd frontend
npm install
copy .env.example .env           # Windows | cp .env.example .env on macOS/Linux
npm run dev
```
App: http://localhost:5173

Register a **patient** account and a **clinician** account (the register page has a role
toggle) to see both sides of the platform.

---

## Quick start (Docker Compose — full stack incl. Redis/ChromaDB)

```bash
# from the project root
copy backend\.env.example backend\.env   # fill in ANTHROPIC_API_KEY
docker compose up -d --build
```
This starts: `postgres-db`, `redis-cache`, `vector-store` (ChromaDB), `backend-api`,
`agent-worker` (scheduled agent jobs), and `frontend-ui`. The frontend container serves
the built static app on port 80; the API is on port 8000.

> Note: `docker/Dockerfile.backend` and `docker/Dockerfile.frontend` referenced by
> `docker-compose.yml` aren't included — add simple Dockerfiles (Python slim + uvicorn for
> the backend, Node build + nginx serve for the frontend) matching your grading environment.

---

## What's implemented end-to-end (tested)

- **Auth:** register/login as `patient` or `doctor`, JWT-protected routes
- **Patient flow:** edit profile → log vitals or upload a lab report (OCR extracts
  biomarkers automatically) → run a multi-disease risk assessment (heart/diabetes/CKD,
  with a SHAP-style "why this score" breakdown) → see it all on a health timeline chart
- **Patient Care Agent:** daily digest banner on the patient dashboard
- **Doctor flow:** prioritized worklist (ranked by severity/escalations/staleness) →
  open a patient's chart → see the Clinician Assist Agent's chart-prep brief → generate a
  draft care plan + medicine candidates (RxNav/openFDA) → approve/modify/reject
- **RAG chatbot:** floating widget on both dashboards, escalates urgent/low-confidence/
  human-requested messages to a doctor or engineer queue instead of guessing
- **Design:** Tailwind design system, Three.js animated hero on the landing page, GSAP
  scroll-reveal and entrance animations throughout

This was verified with a real Playwright run: register → log vitals → run assessment →
see risk gauges populate → doctor worklist shows the patient ranked correctly → chart-prep
brief renders → care plan drafting works.

## Project layout
```
healthsphere/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + router wiring
│   │   ├── core/                # config, JWT/password auth
│   │   ├── db/                  # session, init_db
│   │   ├── models/               # SQLAlchemy models (12 tables)
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── routers/              # auth, patients, doctors, assessments,
│   │   │                         # notifications, agents_and_chat
│   │   ├── services/             # ocr_service, ml_engine, medicine_recommender
│   │   ├── agents/                # patient_agent, doctor_agent, worker (scheduler)
│   │   └── chatbot/               # rag_pipeline, seed_knowledge_base
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/client.js          # axios client, one function per endpoint
│   │   ├── context/AuthContext.jsx
│   │   ├── components/            # layout, ChatWidget, RiskGauge, VitalsChart, three/
│   │   ├── pages/                 # Landing, Login, Register, patient/, doctor/
│   │   └── App.jsx
│   └── package.json
├── db/healthsphere.db             # SQLite database (schema pre-applied)
├── docker-compose.yml
└── setup_env.bat
```

## Known gaps to finish for submission
- `docker/Dockerfile.backend` / `Dockerfile.frontend` aren't included — add them, or just
  run frontend/backend locally with the Quick Start steps above (no Docker needed).
- The medicine-recommendation demo mapping (`CONDITION_TO_DRUG_CLASS` in
  `medicine_recommender.py`) is intentionally simple — review with a faculty/clinical
  advisor before presenting it as clinically validated.
- RxNav/openFDA calls need normal internet access (they were blocked in the sandbox this
  was built in, but will work on your machine/school network).
- The ML engine (`services/ml_engine.py`) uses transparent rule thresholds instead of a
  trained XGBoost model, so the whole pipeline runs without needing MIMIC-III access —
  swap in a trained model later without changing any other layer.
