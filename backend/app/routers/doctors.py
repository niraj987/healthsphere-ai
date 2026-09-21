from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_role
from app.db.session import get_db
from app.models.models import CarePlan, PatientProfile, User
from app.schemas.schemas import CarePlanOut, CarePlanReview, PatientProfileOut

router = APIRouter(prefix="/api/doctor", tags=["doctor"])


@router.get("/patients", response_model=list[PatientProfileOut])
def list_all_patients(db: Session = Depends(get_db), user: User = Depends(require_role("doctor", "admin"))):
    profiles = db.query(PatientProfile).all()
    for p in profiles:
        p.full_name = p.user.full_name if p.user else None
    return profiles


@router.get("/patients/{patient_id}/care-plans", response_model=list[CarePlanOut])
def list_care_plans(patient_id: int, db: Session = Depends(get_db), user: User = Depends(require_role("doctor", "admin"))):
    return (
        db.query(CarePlan)
        .filter(CarePlan.patient_id == patient_id)
        .order_by(CarePlan.created_at.desc())
        .all()
    )


@router.put("/care-plans/{plan_id}/review", response_model=CarePlanOut)
def review_care_plan(
    plan_id: int, body: CarePlanReview, db: Session = Depends(get_db), user: User = Depends(require_role("doctor", "admin"))
):
    plan = db.query(CarePlan).get(plan_id)
    if not plan:
        raise HTTPException(404, "Care plan not found")

    plan.approval_status = body.approval_status
    plan.doctor_name = body.doctor_name or user.full_name
    if body.clinical_summary:
        plan.clinical_summary = body.clinical_summary
    if body.lifestyle_guidelines:
        plan.lifestyle_guidelines = body.lifestyle_guidelines

    db.commit()
    db.refresh(plan)
    return plan
