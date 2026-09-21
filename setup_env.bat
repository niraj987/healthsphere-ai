@echo off
setlocal

echo ============================================
echo  HealthSphere AI - Backend Environment Setup
echo ============================================

REM --- 1. Activate virtual environment ---
echo Activating virtual environment...
call backend\venv\Scripts\activate.bat
if errorlevel 1 (
    echo No venv found. Creating one at backend\venv ...
    python -m venv backend\venv
    call backend\venv\Scripts\activate.bat
)

REM --- 2. Install/upgrade dependencies ---
echo Installing dependencies from backend\requirements.txt...
pip install --upgrade pip
pip install -r backend\requirements.txt

REM --- 3. spaCy model needed by the OCR/NLP pipeline (Module 1) ---
echo Downloading spaCy English model...
python -m spacy download en_core_web_sm

REM --- 4. Set up local .env if missing ---
if not exist backend\.env (
    echo Creating backend\.env from template - please fill in your API keys.
    copy backend\.env.example backend\.env
) else (
    echo backend\.env already exists, leaving it as-is.
)

REM --- 5. Create/upgrade database tables (safe: only adds new tables) ---
echo Initializing database (adds agent_tasks, chat_sessions, chat_messages,
echo escalation_tickets, medicine_recommendations if not already present)...
pushd backend
python -m app.db.init_db
popd

REM --- 6. Seed the RAG chatbot knowledge base (requires vector-store container running) ---
echo Seeding chatbot knowledge base (skip if vector-store isn't running yet)...
pushd backend
python -m app.chatbot.seed_knowledge_base
popd

echo ============================================
echo  Setup Complete! Next steps:
echo   1. Fill in ANTHROPIC_API_KEY in backend\.env
echo   2. Run: docker compose up -d
echo   3. Backend docs at http://localhost:8000/docs
echo ============================================

endlocal
