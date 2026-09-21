"""
HealthSphere AI — SQLAlchemy models

This file matches the EXISTING healthsphere.db schema (users, patient_profiles,
notifications, vitals_records, lab_reports, assessment_results, care_plans)
and adds the new tables needed for:

  - AI Agents (Patient Care Agent / Clinician Assist Agent) task logging
  - RAG chatbot conversation history
  - Human-in-the-loop escalation tickets (doctor / engineer review queue)
  - Medicine / drug-information recommendations (decision-support only)

Run `python -m app.db.init_db` (see db/init_db.py) to create the new tables
on top of the existing healthsphere.db without touching existing data.
"""

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# ---------------------------------------------------------------------------
# EXISTING TABLES (kept identical to healthsphere.db so this file can be the
# single source of truth going forward)
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String)  # "patient" | "doctor" | "engineer" | "admin"
    created_at = Column(DateTime, default=datetime.utcnow)

    patient_profile = relationship("PatientProfile", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    medical_record_number = Column(String)
    age = Column(Integer)
    gender = Column(String)
    blood_group = Column(String)
    height_cm = Column(Float)
    weight_kg = Column(Float)
    primary_condition = Column(String)

    user = relationship("User", back_populates="patient_profile")
    vitals = relationship("VitalsRecord", back_populates="patient")
    lab_reports = relationship("LabReport", back_populates="patient")
    assessments = relationship("AssessmentResult", back_populates="patient")
    care_plans = relationship("CarePlan", back_populates="patient")
    agent_tasks = relationship("AgentTask", back_populates="patient")
    escalations = relationship("EscalationTicket", back_populates="patient")
    medicine_recommendations = relationship("MedicineRecommendation", back_populates="patient")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class VitalsRecord(Base):
    __tablename__ = "vitals_records"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    systolic_bp = Column(Float)
    diastolic_bp = Column(Float)
    heart_rate = Column(Float)
    fasting_glucose = Column(Float)
    cholesterol = Column(Float)
    serum_creatinine = Column(Float)
    bmi = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("PatientProfile", back_populates="vitals")


class LabReport(Base):
    __tablename__ = "lab_reports"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    filename = Column(String)
    extracted_biomarkers = Column(JSON)
    raw_ocr_snippet = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("PatientProfile", back_populates="lab_reports")


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    overall_risk_score = Column(Float)
    overall_severity = Column(String)
    heart_risk_pct = Column(Float)
    diabetes_risk_pct = Column(Float)
    ckd_risk_pct = Column(Float)
    shap_explanation = Column(JSON)
    assessed_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("PatientProfile", back_populates="assessments")


class CarePlan(Base):
    __tablename__ = "care_plans"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    doctor_name = Column(String)
    clinical_summary = Column(Text)
    prescriptions = Column(JSON)
    lifestyle_guidelines = Column(Text)
    approval_status = Column(String, default="pending")  # pending | approved | modified | rejected
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("PatientProfile", back_populates="care_plans")


# ---------------------------------------------------------------------------
# NEW TABLES
# ---------------------------------------------------------------------------

class AgentTask(Base):
    """
    Log + task queue for the two AI agents:
      - agent_type = "patient_care"  -> reminders, adherence nudges, symptom triage
      - agent_type = "clinician_assist" -> daily patient prioritization, chart prep,
        draft care-plan notes, time-management (who to see first today)
    """
    __tablename__ = "agent_tasks"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    agent_type = Column(String, nullable=False)  # patient_care | clinician_assist
    task_type = Column(String, nullable=False)   # reminder | triage | prioritization | summary
    input_context = Column(JSON)
    output_summary = Column(Text)
    priority = Column(String, default="normal")   # low | normal | high | urgent
    status = Column(String, default="pending")     # pending | completed | dismissed
    scheduled_for = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    patient = relationship("PatientProfile", back_populates="agent_tasks")


class ChatSession(Base):
    """One conversation thread with the RAG health-assistant chatbot."""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="active")  # active | escalated | closed

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String, nullable=False)  # user | assistant | system
    content = Column(Text, nullable=False)
    retrieved_sources = Column(JSON)   # RAG source chunks used to answer
    confidence = Column(Float)         # retrieval/answer confidence score
    was_escalated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")


class EscalationTicket(Base):
    """
    Human-in-the-loop queue. Created automatically when the chatbot:
      - detects an urgent / red-flag symptom description, OR
      - has low retrieval confidence, OR
      - the user explicitly asks for a human
    A ticket is routed to a doctor (clinical questions) or an engineer
    (app/technical problems) and tracked to resolution.
    """
    __tablename__ = "escalation_tickets"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"), nullable=True)
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=True)
    category = Column(String, nullable=False)   # clinical | technical | billing | other
    reason = Column(String, nullable=False)     # low_confidence | red_flag_symptom | user_requested
    summary = Column(Text)
    urgency = Column(String, default="normal")  # normal | high | emergency
    assigned_role = Column(String)              # doctor | engineer
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, default="open")     # open | in_progress | resolved | closed
    resolution_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)

    patient = relationship("PatientProfile", back_populates="escalations")


class MedicineRecommendation(Base):
    """
    Informational drug/medicine suggestions pulled from a public drug-information
    API (RxNav/RxNorm, openFDA) for a given condition/biomarker pattern.
    These are DECISION-SUPPORT ONLY: no dosage is finalized by the AI, and every
    row requires a doctor's explicit approval before it can appear in a CarePlan.
    """
    __tablename__ = "medicine_recommendations"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    assessment_id = Column(Integer, ForeignKey("assessment_results.id"), nullable=True)
    condition = Column(String, nullable=False)          # e.g. "Type 2 Diabetes risk"
    candidate_drug_name = Column(String, nullable=False)
    rxnorm_cui = Column(String)                          # RxNorm concept ID from RxNav
    drug_class = Column(String)
    source_api = Column(String, default="RxNav/RxNorm")
    general_info = Column(Text)                          # plain-language info, NOT a dosage
    interaction_warnings = Column(JSON)
    doctor_status = Column(String, default="pending_review")  # pending_review | approved | rejected
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("PatientProfile", back_populates="medicine_recommendations")
