from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.models import AssessmentResult, PatientProfile, User, VitalsRecord
from app.schemas.schemas import AssessmentOut
from app.services.ml_engine import run_multi_disease_assessment

router = APIRouter(prefix="/api/assessments", tags=["assessments"])


@router.post("/patients/{patient_id}/run", response_model=AssessmentOut)
def run_assessment(patient_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = db.query(PatientProfile).get(patient_id)
    if not profile:
        raise HTTPException(404, "Patient not found")

    latest_vitals = (
        db.query(VitalsRecord)
        .filter(VitalsRecord.patient_id == patient_id)
        .order_by(VitalsRecord.recorded_at.desc())
        .first()
    )
    if not latest_vitals:
        raise HTTPException(400, "No vitals on file yet — add vitals or upload a lab report first")

    result = run_multi_disease_assessment(
        age=profile.age,
        systolic_bp=latest_vitals.systolic_bp,
        diastolic_bp=latest_vitals.diastolic_bp,
        heart_rate=latest_vitals.heart_rate,
        fasting_glucose=latest_vitals.fasting_glucose,
        cholesterol=latest_vitals.cholesterol,
        serum_creatinine=latest_vitals.serum_creatinine,
        bmi=latest_vitals.bmi,
    )

    assessment = AssessmentResult(patient_id=patient_id, assessed_at=datetime.utcnow(), **result)
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.get("/patients/{patient_id}", response_model=list[AssessmentOut])
def list_assessments(patient_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(AssessmentResult)
        .filter(AssessmentResult.patient_id == patient_id)
        .order_by(AssessmentResult.assessed_at.asc())
        .all()
    )


@router.get("/patients/{patient_id}/latest", response_model=AssessmentOut)
def latest_assessment(patient_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    assessment = (
        db.query(AssessmentResult)
        .filter(AssessmentResult.patient_id == patient_id)
        .order_by(AssessmentResult.assessed_at.desc())
        .first()
    )
    if not assessment:
        raise HTTPException(404, "No assessment on file yet")
    return assessment
