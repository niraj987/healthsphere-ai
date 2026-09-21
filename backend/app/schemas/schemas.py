"""Pydantic schemas — request/response shapes for the API."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


# ---------- Auth / Users ----------

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str
    role: str = Field(default="patient", pattern="^(patient|doctor|engineer|admin)$")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Patient profile ----------

class PatientProfileCreate(BaseModel):
    age: int
    gender: str
    blood_group: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    primary_condition: Optional[str] = None


class PatientProfileOut(BaseModel):
    id: int
    user_id: int
    full_name: Optional[str] = None
    medical_record_number: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    blood_group: Optional[str]
    height_cm: Optional[float]
    weight_kg: Optional[float]
    primary_condition: Optional[str]

    class Config:
        from_attributes = True


# ---------- Vitals ----------

class VitalsCreate(BaseModel):
    systolic_bp: Optional[float] = None
    diastolic_bp: Optional[float] = None
    heart_rate: Optional[float] = None
    fasting_glucose: Optional[float] = None
    cholesterol: Optional[float] = None
    serum_creatinine: Optional[float] = None
    bmi: Optional[float] = None


class VitalsOut(VitalsCreate):
    id: int
    patient_id: int
    recorded_at: datetime

    class Config:
        from_attributes = True


# ---------- Lab reports ----------

class LabReportOut(BaseModel):
    id: int
    patient_id: int
    filename: str
    extracted_biomarkers: Optional[dict[str, Any]]
    raw_ocr_snippet: Optional[str]
    uploaded_at: datetime

    class Config:
        from_attributes = True


# ---------- Assessments ----------

class AssessmentOut(BaseModel):
    id: int
    patient_id: int
    overall_risk_score: Optional[float]
    overall_severity: Optional[str]
    heart_risk_pct: Optional[float]
    diabetes_risk_pct: Optional[float]
    ckd_risk_pct: Optional[float]
    shap_explanation: Optional[dict[str, Any]]
    assessed_at: datetime

    class Config:
        from_attributes = True


# ---------- Care plans ----------

class CarePlanReview(BaseModel):
    approval_status: str = Field(pattern="^(approved|modified|rejected)$")
    doctor_name: Optional[str] = None
    clinical_summary: Optional[str] = None
    lifestyle_guidelines: Optional[str] = None


class CarePlanOut(BaseModel):
    id: int
    patient_id: int
    doctor_name: Optional[str]
    clinical_summary: Optional[str]
    prescriptions: Optional[list[dict[str, Any]]]
    lifestyle_guidelines: Optional[str]
    approval_status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Notifications ----------

class NotificationOut(BaseModel):
    id: int
    title: Optional[str]
    message: Optional[str]
    is_read: bool
    timestamp: datetime

    class Config:
        from_attributes = True
