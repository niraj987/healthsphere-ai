"""
HealthSphere AI — Backend Entrypoint
=======================================
Run with:
    uvicorn app.main:app --reload --port 8000

Interactive API docs then live at http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.init_db import init_db
from app.routers import agents_and_chat, assessments, auth, doctors, notifications, patients

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered multi-disease assessment, personalized care, and continuous health "
    "monitoring platform. Clinical decision-support only — not a replacement for a licensed clinician.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(assessments.router)
app.include_router(notifications.router)
app.include_router(agents_and_chat.router, prefix="/api")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {
        "service": settings.APP_NAME,
        "status": "running",
        "docs": "/docs",
        "note": "Clinical decision-support platform — outputs require clinician review.",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
