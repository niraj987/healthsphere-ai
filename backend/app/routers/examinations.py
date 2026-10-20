"""
API Endpoints for Clinical ML Examinations:
- Breast Cancer Examination (Wisconsin FNA Diagnostic RF)
- Oncology & Cancer Cytology Screening (GBM)
- Heart Disease Examination (Cleveland Cardiovascular RF)
- Diabetes & Metabolic Examination (Pima RF)
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.models import ClinicalExaminationRecord, PatientProfile, User
from app.services.clinical_models import (
    get_model,
    predict_breast_cancer,
    predict_cancer_screening,
    predict_heart_disease,
    predict_diabetes,
    train_and_save_all_models,
)

router = APIRouter(prefix="/api/examinations", tags=["examinations"])


class ExaminationPredictionRequest(BaseModel):
    patient_id: Optional[int] = None
    features: Dict[str, Any]


class SaveExaminationRequest(BaseModel):
    patient_id: Optional[int] = None
    examination_type: str
    title: str
    predicted_class: str
    risk_percentage: float
    confidence_percentage: float
    severity: str
    recommendation: Optional[str] = None
    input_features: Dict[str, Any]
    contributing_factors: Optional[List[Dict[str, Any]]] = None
    model_metrics: Optional[Dict[str, Any]] = None
    doctor_notes: Optional[str] = None


@router.get("/models")
def get_all_models_info():
    """Retrieve performance metrics and dataset specifications for all clinical models."""
    models_info = {}
    for key in ["breast_cancer", "cancer", "heart", "diabetes"]:
        try:
            bundle = get_model(key)
            models_info[key] = bundle["metrics"]
        except Exception as e:
            models_info[key] = {"error": str(e)}
    return models_info


@router.post("/breast-cancer/predict")
def run_breast_cancer_examination(req: ExaminationPredictionRequest):
    """Run diagnostic prediction on breast cancer morphometric markers."""
    try:
        return predict_breast_cancer(req.features)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Breast cancer prediction error: {str(e)}")


@router.post("/cancer/predict")
def run_cancer_screening(req: ExaminationPredictionRequest):
    """Run cytology screening for general cancer / cellular atypia markers."""
    try:
        return predict_cancer_screening(req.features)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cancer screening error: {str(e)}")


@router.post("/heart-disease/predict")
def run_heart_disease_examination(req: ExaminationPredictionRequest):
    """Run cardiovascular risk prediction using clinical heart disease biomarkers."""
    try:
        return predict_heart_disease(req.features)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Heart disease prediction error: {str(e)}")


@router.post("/diabetes/predict")
def run_diabetes_examination(req: ExaminationPredictionRequest):
    """Run metabolic / diabetes prediction using glucose and physiological markers."""
    try:
        return predict_diabetes(req.features)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Diabetes prediction error: {str(e)}")


@router.get("/sample-cases/{disease_type}")
def get_sample_cases(disease_type: str):
    """Return pre-configured realistic low-risk and high-risk clinical test cases."""
    samples = {
        "breast_cancer": {
            "low_risk": {
                "mean radius": 11.42, "mean texture": 15.22, "mean perimeter": 73.18, "mean area": 402.8,
                "mean smoothness": 0.085, "mean compactness": 0.056, "mean concavity": 0.024,
                "mean concave points": 0.019, "mean symmetry": 0.162, "mean fractal dimension": 0.058,
                "worst radius": 12.56, "worst texture": 19.85, "worst perimeter": 81.25, "worst area": 485.0,
                "worst smoothness": 0.115, "worst compactness": 0.112, "worst concavity": 0.089,
                "worst concave points": 0.052, "worst symmetry": 0.245, "worst fractal dimension": 0.072
            },
            "high_risk": {
                "mean radius": 20.57, "mean texture": 21.6, "mean perimeter": 134.7, "mean area": 1290.0,
                "mean smoothness": 0.114, "mean compactness": 0.236, "mean concavity": 0.282,
                "mean concave points": 0.147, "mean symmetry": 0.221, "mean fractal dimension": 0.078,
                "worst radius": 25.42, "worst texture": 28.5, "worst perimeter": 172.0, "worst area": 1950.0,
                "worst smoothness": 0.162, "worst compactness": 0.584, "worst concavity": 0.655,
                "worst concave points": 0.265, "worst symmetry": 0.412, "worst fractal dimension": 0.115
            }
        },
        "cancer": {
            "low_risk": {
                "mean radius": 12.05, "mean texture": 16.4, "mean perimeter": 77.2, "mean area": 450.0,
                "mean smoothness": 0.088, "mean compactness": 0.062, "mean concavity": 0.031,
                "mean concave points": 0.021, "mean symmetry": 0.171, "mean fractal dimension": 0.059
            },
            "high_risk": {
                "mean radius": 19.8, "mean texture": 24.5, "mean perimeter": 130.0, "mean area": 1200.0,
                "mean smoothness": 0.118, "mean compactness": 0.220, "mean concavity": 0.245,
                "mean concave points": 0.135, "mean symmetry": 0.230, "mean fractal dimension": 0.075
            }
        },
        "heart_disease": {
            "low_risk": {
                "age": 38, "sex": 0, "cp": 1, "trestbps": 116, "chol": 180,
                "fbs": 0, "restecg": 0, "thalach": 172, "exang": 0, "oldpeak": 0.0,
                "slope": 2, "ca": 0, "thal": 2
            },
            "high_risk": {
                "age": 67, "sex": 1, "cp": 0, "trestbps": 160, "chol": 286,
                "fbs": 1, "restecg": 0, "thalach": 108, "exang": 1, "oldpeak": 2.6,
                "slope": 1, "ca": 3, "thal": 2
            }
        },
        "diabetes": {
            "low_risk": {
                "Pregnancies": 1, "Glucose": 88, "BloodPressure": 68, "SkinThickness": 22,
                "Insulin": 75, "BMI": 22.4, "DiabetesPedigreeFunction": 0.25, "Age": 28
            },
            "high_risk": {
                "Pregnancies": 6, "Glucose": 172, "BloodPressure": 86, "SkinThickness": 38,
                "Insulin": 240, "BMI": 36.8, "DiabetesPedigreeFunction": 0.88, "Age": 54
            }
        }
    }

    if disease_type not in samples:
        raise HTTPException(status_code=404, detail="Unknown examination type")
    return samples[disease_type]


@router.post("/save")
def save_examination_record(req: SaveExaminationRequest, db: Session = Depends(get_db)):
    """Save an examination result to the database."""
    record = ClinicalExaminationRecord(
        patient_id=req.patient_id,
        examination_type=req.examination_type,
        title=req.title,
        predicted_class=req.predicted_class,
        risk_percentage=req.risk_percentage,
        confidence_percentage=req.confidence_percentage,
        severity=req.severity,
        recommendation=req.recommendation,
        input_features=req.input_features,
        contributing_factors=req.contributing_factors,
        model_metrics=req.model_metrics,
        doctor_notes=req.doctor_notes,
        created_at=datetime.utcnow()
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {
        "status": "success",
        "id": record.id,
        "message": f"{req.title} successfully recorded."
    }


@router.get("/patients/{patient_id}")
def list_patient_examinations(patient_id: int, db: Session = Depends(get_db)):
    """Retrieve all diagnostic examinations for a patient."""
    records = (
        db.query(ClinicalExaminationRecord)
        .filter(ClinicalExaminationRecord.patient_id == patient_id)
        .order_by(ClinicalExaminationRecord.created_at.desc())
        .all()
    )
    return records


@router.get("/recent")
def list_recent_examinations(limit: int = 10, db: Session = Depends(get_db)):
    """Retrieve recent clinical examinations across all patients."""
    records = (
        db.query(ClinicalExaminationRecord)
        .order_by(ClinicalExaminationRecord.created_at.desc())
        .limit(limit)
        .all()
    )
    return records
