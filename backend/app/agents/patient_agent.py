"""
Patient Care Agent
===================
Helps the PATIENT with time-management and understanding their own care:

  1. Daily digest: "here's what's due today" (medication, follow-up tests,
     appointments) built from care_plans + notifications.
  2. Adherence nudges: detects missed reminders and drafts a friendly nudge.
  3. Plain-language explainer: turns a SHAP explanation / risk score into a
     short, non-alarming summary the patient can actually understand.
  4. Symptom triage hand-off: if the patient describes a concerning symptom
     while chatting, the agent classifies urgency and creates an
     EscalationTicket instead of guessing at a diagnosis itself.

The agent NEVER changes a CarePlan, NEVER finalizes a diagnosis, and NEVER
tells the patient to stop/start a medication on its own — it only summarizes,
reminds, and escalates.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.models import (
    AgentTask,
    CarePlan,
    EscalationTicket,
    Notification,
    PatientProfile,
)

# Symptom phrases that always trigger an urgent human hand-off rather than
# a chatbot-only answer. Keep this list short, literal, and reviewed by a
# clinician advisor — it is a safety net, not a diagnostic tool.
RED_FLAG_PHRASES = [
    "chest pain", "can't breathe", "cannot breathe", "shortness of breath",
    "severe bleeding", "fainted", "loss of consciousness", "suicidal",
    "seizure", "one side of my face", "slurred speech", "severe allergic",
]


@dataclass
class DailyDigest:
    patient_id: int
    due_today: list[str]
    overdue: list[str]
    plain_summary: str


def build_daily_digest(db: Session, patient_id: int) -> DailyDigest:
    """Assemble the patient's 'what matters today' list — the time-management core."""
    today = datetime.utcnow().date()

    plan = (
        db.query(CarePlan)
        .filter(CarePlan.patient_id == patient_id, CarePlan.approval_status == "approved")
        .order_by(CarePlan.created_at.desc())
        .first()
    )

    pending_tasks = (
        db.query(AgentTask)
        .filter(
            AgentTask.patient_id == patient_id,
            AgentTask.agent_type == "patient_care",
            AgentTask.status == "pending",
        )
        .all()
    )

    due_today, overdue = [], []
    for task in pending_tasks:
        label = task.output_summary or task.task_type
        if task.scheduled_for and task.scheduled_for.date() < today:
            overdue.append(label)
        else:
            due_today.append(label)

    summary_bits = []
    if plan:
        summary_bits.append(f"Your active care plan: {plan.lifestyle_guidelines or plan.clinical_summary}")
    if overdue:
        summary_bits.append(f"You have {len(overdue)} overdue item(s) — please catch up when you can.")
    if due_today:
        summary_bits.append(f"{len(due_today)} item(s) due today.")
    if not summary_bits:
        summary_bits.append("Nothing urgent today — keep up the good work!")

    return DailyDigest(
        patient_id=patient_id,
        due_today=due_today,
        overdue=overdue,
        plain_summary=" ".join(summary_bits),
    )


def draft_adherence_nudge(db: Session, patient_id: int, missed_task: AgentTask) -> Notification:
    """Create a friendly (not guilt-tripping) reminder notification for a missed task."""
    message = (
        f"Hi! It looks like you haven't marked \"{missed_task.output_summary or missed_task.task_type}\" "
        "as done yet. No worries if life got busy — just tap it in your portal once it's complete, "
        "or let us know if something's stopping you and we'll help."
    )
    patient = db.query(PatientProfile).get(patient_id)
    notification = Notification(
        user_id=patient.user_id if patient else None,
        title="Friendly reminder",
        message=message,
        is_read=False,
        timestamp=datetime.utcnow(),
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def explain_risk_in_plain_language(overall_severity: str, top_factors: list[str]) -> str:
    """Turn SHAP-style top factors into a short, calm, non-alarming explanation."""
    factors_text = ", ".join(top_factors[:3]) if top_factors else "your recent readings"
    return (
        f"Your latest assessment came back as **{overall_severity.lower()}** risk. "
        f"This is mainly influenced by {factors_text}. This is a screening signal, not a diagnosis — "
        "your doctor will review it and decide on next steps together with you."
    )


def screen_message_for_red_flags(message: str) -> bool:
    lowered = message.lower()
    return any(phrase in lowered for phrase in RED_FLAG_PHRASES)


def handle_patient_message(db: Session, patient_id: int, chat_session_id: int, message: str) -> EscalationTicket | None:
    """
    Call this BEFORE letting the RAG chatbot answer. If a red-flag symptom is
    detected, skip the chatbot's own generated answer and escalate immediately.
    """
    if not screen_message_for_red_flags(message):
        return None

    ticket = EscalationTicket(
        patient_id=patient_id,
        chat_session_id=chat_session_id,
        category="clinical",
        reason="red_flag_symptom",
        summary=f"Patient message flagged for urgent review: \"{message[:300]}\"",
        urgency="emergency",
        assigned_role="doctor",
        status="open",
        created_at=datetime.utcnow(),
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def schedule_reminder(db: Session, patient_id: int, label: str, due_in_hours: int, priority: str = "normal") -> AgentTask:
    task = AgentTask(
        patient_id=patient_id,
        agent_type="patient_care",
        task_type="reminder",
        output_summary=label,
        priority=priority,
        status="pending",
        scheduled_for=datetime.utcnow() + timedelta(hours=due_in_hours),
        created_at=datetime.utcnow(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
