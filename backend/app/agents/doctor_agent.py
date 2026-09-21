"""
Clinician Assist Agent
========================
Helps the DOCTOR manage time and review load:

  1. Prioritized worklist: ranks the doctor's patients by risk severity,
     days-since-last-review, and open escalation tickets — answers
     "who should I look at first today."
  2. Chart-prep brief: one-paragraph summary of a patient (latest vitals,
     risk trend, open escalations) so the doctor isn't re-reading the
     whole history before every consult.
  3. Draft care-plan assembly: pulls approved-pending MedicineRecommendation
     candidates + lifestyle notes into a DRAFT CarePlan the doctor can edit
     and approve — the agent never sets approval_status to "approved" itself.
  4. Escalation triage: surfaces open EscalationTickets assigned to doctors,
     sorted by urgency.

Everything this agent produces is a DRAFT or a SORTED VIEW. No care plan,
prescription, or diagnosis becomes final without a doctor explicitly
approving it (see CarePlan.approval_status and MedicineRecommendation.doctor_status).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.models import (
    AssessmentResult,
    CarePlan,
    EscalationTicket,
    MedicineRecommendation,
    PatientProfile,
)

SEVERITY_WEIGHT = {"high": 3, "moderate": 2, "low": 1}


@dataclass
class WorklistItem:
    patient_id: int
    patient_name: str
    severity: str
    days_since_last_assessment: int
    open_escalations: int
    priority_score: float


def build_prioritized_worklist(db: Session, limit: int = 25) -> list[WorklistItem]:
    """
    The doctor's time-management view: 'who do I see first today'.
    priority_score = severity weight + escalation weight + staleness weight
    """
    items: list[WorklistItem] = []
    patients = db.query(PatientProfile).all()

    for patient in patients:
        latest_assessment = (
            db.query(AssessmentResult)
            .filter(AssessmentResult.patient_id == patient.id)
            .order_by(AssessmentResult.assessed_at.desc())
            .first()
        )
        if not latest_assessment:
            continue

        days_since = (datetime.utcnow() - latest_assessment.assessed_at).days if latest_assessment.assessed_at else 999
        open_escalations = (
            db.query(EscalationTicket)
            .filter(
                EscalationTicket.patient_id == patient.id,
                EscalationTicket.status.in_(["open", "in_progress"]),
            )
            .count()
        )

        severity = (latest_assessment.overall_severity or "low").lower()
        score = (
            SEVERITY_WEIGHT.get(severity, 1) * 10
            + open_escalations * 15
            + min(days_since, 30) * 0.5
        )

        items.append(
            WorklistItem(
                patient_id=patient.id,
                patient_name=patient.user.full_name if patient.user else f"Patient #{patient.id}",
                severity=severity,
                days_since_last_assessment=days_since,
                open_escalations=open_escalations,
                priority_score=round(score, 1),
            )
        )

    items.sort(key=lambda i: i.priority_score, reverse=True)
    return items[:limit]


def build_chart_prep_brief(db: Session, patient_id: int) -> str:
    patient = db.query(PatientProfile).get(patient_id)
    if not patient:
        return "Patient not found."

    latest_assessment = (
        db.query(AssessmentResult)
        .filter(AssessmentResult.patient_id == patient_id)
        .order_by(AssessmentResult.assessed_at.desc())
        .first()
    )
    open_tickets = (
        db.query(EscalationTicket)
        .filter(EscalationTicket.patient_id == patient_id, EscalationTicket.status == "open")
        .all()
    )

    lines = [f"Patient: {patient.user.full_name if patient.user else patient.id} "
             f"({patient.age}y, {patient.gender}, primary condition: {patient.primary_condition or 'n/a'})"]

    if latest_assessment:
        lines.append(
            f"Latest risk assessment ({latest_assessment.assessed_at:%Y-%m-%d}): "
            f"overall {latest_assessment.overall_severity}, "
            f"heart {latest_assessment.heart_risk_pct}%, "
            f"diabetes {latest_assessment.diabetes_risk_pct}%, "
            f"CKD {latest_assessment.ckd_risk_pct}%."
        )
    else:
        lines.append("No assessment on file yet.")

    if open_tickets:
        lines.append(f"⚠ {len(open_tickets)} open escalation ticket(s): "
                      + "; ".join(t.summary[:80] for t in open_tickets))

    return "\n".join(lines)


def draft_care_plan_from_recommendations(db: Session, patient_id: int, assessment_id: int) -> CarePlan:
    """
    Assemble a DRAFT care plan from pending MedicineRecommendation rows plus a
    generic lifestyle note. Saved with approval_status='pending' — the doctor
    must review and click Approve/Modify in the Clinician Dashboard (Module 5)
    before it becomes active. Mirrors workflow Step 5 in the project proposal.
    """
    candidates = (
        db.query(MedicineRecommendation)
        .filter(
            MedicineRecommendation.patient_id == patient_id,
            MedicineRecommendation.assessment_id == assessment_id,
            MedicineRecommendation.doctor_status == "pending_review",
        )
        .all()
    )

    prescriptions_payload = [
        {
            "drug_class": c.drug_class,
            "candidate_drug_name": c.candidate_drug_name,
            "general_info": c.general_info,
            "warnings": c.interaction_warnings,
            "source": c.source_api,
            "status": "AWAITING_DOCTOR_APPROVAL",
        }
        for c in candidates
    ]

    plan = CarePlan(
        patient_id=patient_id,
        doctor_name=None,  # filled in when a doctor claims/approves it
        clinical_summary="Auto-drafted by Clinician Assist Agent from latest risk assessment. "
                          "Review required before activation.",
        prescriptions=prescriptions_payload,
        lifestyle_guidelines="Standard lifestyle guidance pending clinician customization "
                              "(diet, activity, follow-up interval).",
        approval_status="pending",
        created_at=datetime.utcnow(),
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def open_doctor_escalations(db: Session, limit: int = 25) -> list[EscalationTicket]:
    urgency_rank = {"emergency": 0, "high": 1, "normal": 2}
    tickets = (
        db.query(EscalationTicket)
        .filter(EscalationTicket.assigned_role == "doctor", EscalationTicket.status == "open")
        .all()
    )
    tickets.sort(key=lambda t: urgency_rank.get(t.urgency, 3))
    return tickets[:limit]
