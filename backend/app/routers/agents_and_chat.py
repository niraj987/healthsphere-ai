"""
FastAPI routes tying the new features into the existing backend-api service.

Mount this in your main FastAPI app with:
    from app.routers.agents_and_chat import router as agents_router
    app.include_router(agents_router, prefix="/api")

Assumes a `get_db()` dependency exists elsewhere in your app (yields a
SQLAlchemy Session) — wire it up to whatever session factory Module 6 /
DevOps has already set up for the backend-api service.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents import doctor_agent, patient_agent
from app.chatbot.rag_pipeline import answer_user_message
from app.db.session import get_db  # implement alongside your existing DB setup
from app.models.models import ChatSession, EscalationTicket
from app.services import medicine_recommender

router = APIRouter(tags=["agents-and-chat"])


# ---------------------------------------------------------------------------
# Patient Care Agent
# ---------------------------------------------------------------------------

@router.get("/patients/{patient_id}/daily-digest")
def get_daily_digest(patient_id: int, db: Session = Depends(get_db)):
    digest = patient_agent.build_daily_digest(db, patient_id)
    return digest


@router.post("/patients/{patient_id}/reminders")
def create_reminder(patient_id: int, label: str, due_in_hours: int = 24, db: Session = Depends(get_db)):
    task = patient_agent.schedule_reminder(db, patient_id, label, due_in_hours)
    return {"id": task.id, "scheduled_for": task.scheduled_for}


# ---------------------------------------------------------------------------
# Clinician Assist Agent
# ---------------------------------------------------------------------------

@router.get("/doctor/worklist")
def get_worklist(limit: int = 25, db: Session = Depends(get_db)):
    return doctor_agent.build_prioritized_worklist(db, limit=limit)


@router.get("/doctor/patients/{patient_id}/chart-prep")
def get_chart_prep(patient_id: int, db: Session = Depends(get_db)):
    return {"brief": doctor_agent.build_chart_prep_brief(db, patient_id)}


@router.post("/doctor/patients/{patient_id}/draft-care-plan")
def create_draft_care_plan(patient_id: int, assessment_id: int, db: Session = Depends(get_db)):
    plan = doctor_agent.draft_care_plan_from_recommendations(db, patient_id, assessment_id)
    return {"care_plan_id": plan.id, "status": plan.approval_status}


@router.get("/doctor/escalations")
def get_doctor_escalations(db: Session = Depends(get_db)):
    return doctor_agent.open_doctor_escalations(db)


# ---------------------------------------------------------------------------
# Medicine / drug-information recommendations (decision-support only)
# ---------------------------------------------------------------------------

@router.post("/patients/{patient_id}/medicine-recommendations")
def generate_medicine_recommendations(patient_id: int, assessment_id: int, db: Session = Depends(get_db)):
    from app.models.models import AssessmentResult

    assessment = db.query(AssessmentResult).get(assessment_id)
    if not assessment:
        raise HTTPException(404, "Assessment not found")

    candidates = medicine_recommender.recommend_for_risk_profile(
        heart_risk_pct=assessment.heart_risk_pct,
        diabetes_risk_pct=assessment.diabetes_risk_pct,
        ckd_risk_pct=assessment.ckd_risk_pct,
    )
    rows = medicine_recommender.to_db_rows(candidates, patient_id, assessment_id)
    db.add_all(rows)
    db.commit()
    return {"created": len(rows), "status": "pending_review"}


class MedicineReviewRequest(BaseModel):
    doctor_status: str  # "approved" | "rejected"
    reviewer_user_id: int


@router.post("/medicine-recommendations/{rec_id}/review")
def review_medicine_recommendation(rec_id: int, body: MedicineReviewRequest, db: Session = Depends(get_db)):
    from app.models.models import MedicineRecommendation

    rec = db.query(MedicineRecommendation).get(rec_id)
    if not rec:
        raise HTTPException(404, "Recommendation not found")
    if body.doctor_status not in {"approved", "rejected"}:
        raise HTTPException(400, "doctor_status must be 'approved' or 'rejected'")

    rec.doctor_status = body.doctor_status
    rec.reviewed_by = body.reviewer_user_id
    db.commit()
    return {"id": rec.id, "doctor_status": rec.doctor_status}


# ---------------------------------------------------------------------------
# RAG Chatbot
# ---------------------------------------------------------------------------

class ChatMessageRequest(BaseModel):
    user_id: int
    session_id: int | None = None
    message: str


@router.post("/chat/message")
def post_chat_message(body: ChatMessageRequest, db: Session = Depends(get_db)):
    if body.session_id:
        session = db.query(ChatSession).get(body.session_id)
        if not session:
            raise HTTPException(404, "Chat session not found")
    else:
        session = ChatSession(user_id=body.user_id, started_at=datetime.utcnow(), last_active_at=datetime.utcnow())
        db.add(session)
        db.commit()
        db.refresh(session)

    answer = answer_user_message(db, session, body.message)
    return {
        "session_id": session.id,
        "reply": answer.text,
        "confidence": answer.confidence,
        "sources": answer.sources,
        "escalated": answer.escalated,
        "ticket_id": answer.ticket_id,
    }


@router.get("/chat/escalations/{ticket_id}")
def get_escalation(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(EscalationTicket).get(ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    return ticket
