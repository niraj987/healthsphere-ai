from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.models import LabReport, PatientProfile, User, VitalsRecord
from app.schemas.schemas import (
    LabReportOut,
    PatientProfileCreate,
    PatientProfileOut,
    VitalsCreate,
    VitalsOut,
)
from app.services import ocr_service

router = APIRouter(prefix="/api/patients", tags=["patients"])

def _with_full_name(profile: PatientProfile) -> PatientProfile:
    profile.full_name = profile.user.full_name if profile.user else None
    return profile



def _get_own_profile(db: Session, user: User) -> PatientProfile:
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(404, "Patient profile not found")
    return profile


@router.get("/me", response_model=PatientProfileOut)
def get_my_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _with_full_name(_get_own_profile(db, user))


@router.put("/me", response_model=PatientProfileOut)
def update_my_profile(body: PatientProfileCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = _get_own_profile(db, user)
    for field, value in body.model_dump().items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return _with_full_name(profile)


@router.get("/{patient_id}", response_model=PatientProfileOut)
def get_patient(patient_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = db.query(PatientProfile).get(patient_id)
    if not profile:
        raise HTTPException(404, "Patient not found")
    return _with_full_name(profile)


@router.post("/me/vitals", response_model=VitalsOut)
def add_vitals(body: VitalsCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = _get_own_profile(db, user)
    record = VitalsRecord(patient_id=profile.id, recorded_at=datetime.utcnow(), **body.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/me/vitals", response_model=list[VitalsOut])
def list_my_vitals(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = _get_own_profile(db, user)
    return (
        db.query(VitalsRecord)
        .filter(VitalsRecord.patient_id == profile.id)
        .order_by(VitalsRecord.recorded_at.asc())
        .all()
    )


@router.get("/{patient_id}/vitals", response_model=list[VitalsOut])
def list_patient_vitals(patient_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(VitalsRecord)
        .filter(VitalsRecord.patient_id == patient_id)
        .order_by(VitalsRecord.recorded_at.asc())
        .all()
    )


@router.post("/me/lab-reports", response_model=LabReportOut)
async def upload_lab_report(
    file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    profile = _get_own_profile(db, user)
    file_bytes = await file.read()
    result = ocr_service.process_upload(file_bytes, file.filename or "upload")

    report = LabReport(
        patient_id=profile.id,
        filename=file.filename or "upload",
        extracted_biomarkers=result["biomarkers"],
        raw_ocr_snippet=result["raw_text"],
        uploaded_at=datetime.utcnow(),
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    # Auto-log any extracted biomarkers as a vitals record too, so the
    # health timeline and risk engine pick them up without manual re-entry.
    biomarkers = result["biomarkers"]
    if biomarkers:
        db.add(
            VitalsRecord(
                patient_id=profile.id,
                systolic_bp=biomarkers.get("systolic_bp"),
                diastolic_bp=biomarkers.get("diastolic_bp"),
                fasting_glucose=biomarkers.get("fasting_glucose"),
                cholesterol=biomarkers.get("cholesterol"),
                serum_creatinine=biomarkers.get("serum_creatinine"),
                bmi=biomarkers.get("bmi"),
                recorded_at=datetime.utcnow(),
            )
        )
        db.commit()

    return report


@router.get("/me/lab-reports", response_model=list[LabReportOut])
def list_my_lab_reports(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = _get_own_profile(db, user)
    return (
        db.query(LabReport)
        .filter(LabReport.patient_id == profile.id)
        .order_by(LabReport.uploaded_at.desc())
        .all()
    )
