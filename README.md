# HealthSphere AI — Full-Stack Capstone Project

An AI-assisted, multi-disease clinical decision-support platform with a **React 19** frontend and a **FastAPI** backend. Patients log vitals/upload lab reports, get an explainable multi-disease risk score, and are supported by a Patient Care Agent; doctors get a prioritized worklist from a Clinician Assist Agent, draft care plans with medicine decision-support, and review/approve everything.

---

## 🛠️ Prerequisites

Before starting the project in VS Code, ensure you have installed:
1. **VS Code (Visual Studio Code):** [Download VS Code](https://code.visualstudio.com/)
2. **Python (v3.10+):** [Download Python](https://www.python.org/downloads/)
3. **Node.js (v18+ or v20+):** [Download Node.js](https://nodejs.org/)

---

## 💻 Step-by-Step Guide: Running in VS Code

### Step 1: Open the Project in VS Code
1. Launch **VS Code**.
2. Go to `File` → `Open Folder...` (or press `Ctrl + K, Ctrl + O`).
3. Select the `healthsphere` root project directory.

---

### Step 2: Open Integrated Terminal
Press `Ctrl + ~` (or `Ctrl + '`) or select `Terminal` → `New Terminal` from the top menu in VS Code.

---

### Step 3: Setup & Run the Backend Server (Terminal 1)

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create a Python virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
     *(If PowerShell blocks execution, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first)*
   - **Windows (Command Prompt):**
     ```cmd
     venv\Scripts\activate.bat
     ```
   - **macOS / Linux:**
     ```bash
     source venv/bin/activate
     ```

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Setup environment configuration (`.env`):
   - **Windows:** `copy .env.example .env`
   - **macOS / Linux:** `cp .env.example .env`

6. Initialize database schema tables:
   ```bash
   python -m app.db.init_db
   ```

7. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - ⚡ **Backend API Endpoint:** [http://localhost:8000](http://localhost:8000)
   - 📖 **Interactive API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Step 4: Setup & Run the Frontend App (Terminal 2)

1. Open a **new terminal tab** in VS Code (click the **`+`** icon in the VS Code Terminal panel).

2. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

3. Setup environment configuration (`.env`):
   - **Windows:** `copy .env.example .env`
   - **macOS / Linux:** `cp .env.example .env`

4. Install Node.js dependencies:
   ```bash
   npm install
   ```

5. Start the React Vite dev server:
   ```bash
   npm run dev
   ```
   - 🚀 **Live Web Application:** [http://localhost:5173](http://localhost:5173)

---

## 🧪 How to Test the Application

1. Open [http://localhost:5173](http://localhost:5173) in your browser.
2. **Patient Workflow:**
   - Click **Register** → Choose **Patient** role.
   - Fill in profile details, enter vitals (Blood Pressure, Glucose, BMI), or upload a lab report.
   - Click **Run Risk Assessment** to view multi-disease risk scores (Heart Disease, Diabetes, CKD) with SHAP-style breakdown.
3. **Doctor Workflow:**
   - Log out and click **Register** → Choose **Doctor** role.
   - View the **Prioritized Worklist** (ranked by patient risk severity).
   - Open a patient chart to view the **Clinician Assist Agent** summary.
   - Click **Draft Care Plan** to review AI medicine recommendations and approve/modify them.

---

## 🐋 Option 2: Running via Docker Compose

If Docker Desktop is installed, start the complete stack with one command from the project root:

```bash
docker compose up -d --build
```
- **Frontend UI:** `http://localhost:80`
- **Backend API:** `http://localhost:8000`

---

## 📁 Project Layout

```
healthsphere/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entrypoint
│   │   ├── core/                # Configuration & JWT authentication
│   │   ├── db/                  # Session setup & database init
│   │   ├── models/               # SQLAlchemy database models
│   │   ├── schemas/              # Pydantic validation schemas
│   │   ├── routers/              # API endpoints (auth, patients, doctors)
│   │   ├── services/             # OCR, ML risk engine & medicine recommender
│   │   ├── agents/                # Patient Care & Clinician Assist Agents
│   │   └── chatbot/               # RAG chatbot & vector store seeding
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/client.js          # Axios API endpoints integration
│   │   ├── components/            # UI components (RiskGauge, VitalsChart)
│   │   ├── pages/                 # Landing, Login, Register, Patient & Doctor views
│   │   └── App.jsx
│   └── package.json
├── docker/                        # Backend & Frontend Dockerfiles
├── db/healthsphere.db             # Local SQLite database
└── docker-compose.yml
```
