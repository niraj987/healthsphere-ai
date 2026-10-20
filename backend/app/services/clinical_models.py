"""
Clinical ML Service for Smart Hospital Management
Trains, caches, and provides inference for:
1. Breast Cancer Examination (Wisconsin Diagnostic - FNA biopsy morphometry)
2. Comprehensive Cancer Examination (Cell nuclei morphology screening)
3. Heart Disease Examination (Cleveland Cardiovascular Dataset)
4. Diabetes & Metabolic Examination (Pima Dataset)
"""

from __future__ import annotations
import os
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, precision_score, recall_score

logger = logging.getLogger("smart_hospital.clinical_models")

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
MODELS_DIR = BASE_DIR / "models" / "trained"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Cache for loaded models in memory
_MODEL_CACHE: Dict[str, Dict[str, Any]] = {}


def train_and_save_all_models(force: bool = False) -> Dict[str, Any]:
    """Train all clinical ML models from the provided CSV datasets and save them."""
    results = {}
    results["breast_cancer"] = _train_breast_cancer_model(force=force)
    results["cancer"] = _train_cancer_screening_model(force=force)
    results["heart"] = _train_heart_model(force=force)
    results["diabetes"] = _train_diabetes_model(force=force)
    return results


def _train_breast_cancer_model(force: bool = False) -> Dict[str, Any]:
    model_path = MODELS_DIR / "breast_cancer_model.joblib"
    if model_path.exists() and not force:
        return joblib.load(model_path)["metrics"]

    csv_path = DATASET_DIR / "breast_cancer.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing {csv_path}")

    df = pd.read_csv(csv_path)
    X = df.drop(columns=["target"])
    # In Wisconsin dataset, 0 = Malignant, 1 = Benign.
    # Convert so that 1 = Malignant (positive finding / cancer risk)
    y = (df["target"] == 0).astype(int)

    feature_names = list(X.columns)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    clf = RandomForestClassifier(n_estimators=120, max_depth=6, random_state=42)
    clf.fit(X_train_s, y_train)

    preds = clf.predict(X_test_s)
    probs = clf.predict_proba(X_test_s)[:, 1]

    metrics = {
        "model_name": "Breast Cancer Examination (FNA Biopsy RF)",
        "dataset_samples": len(df),
        "features_count": len(feature_names),
        "accuracy": round(float(accuracy_score(y_test, preds)) * 100, 1),
        "roc_auc": round(float(roc_auc_score(y_test, probs)) * 100, 1),
        "precision": round(float(precision_score(y_test, preds)) * 100, 1),
        "recall": round(float(recall_score(y_test, preds)) * 100, 1),
        "feature_importances": sorted(
            [{"feature": f, "importance": round(float(imp) * 100, 2)}
             for f, imp in zip(feature_names, clf.feature_importances_)],
            key=lambda x: x["importance"],
            reverse=True
        )[:10],
    }

    joblib.dump({
        "model": clf,
        "scaler": scaler,
        "feature_names": feature_names,
        "metrics": metrics,
        "target_mapping": {0: "Benign (Non-Malignant)", 1: "Malignant (Carcinoma)"}
    }, model_path)

    _MODEL_CACHE["breast_cancer"] = joblib.load(model_path)
    return metrics


def _train_cancer_screening_model(force: bool = False) -> Dict[str, Any]:
    """
    Oncology / General Cancer Cytology Screening Model.
    Focuses on the primary 10 morphometric cell nuclei features:
    mean radius, texture, perimeter, area, smoothness, compactness,
    concavity, concave points, symmetry, fractal dimension.
    """
    model_path = MODELS_DIR / "cancer_screening_model.joblib"
    if model_path.exists() and not force:
        return joblib.load(model_path)["metrics"]

    csv_path = DATASET_DIR / "breast_cancer.csv"
    df = pd.read_csv(csv_path)

    core_features = [
        "mean radius", "mean texture", "mean perimeter", "mean area",
        "mean smoothness", "mean compactness", "mean concavity",
        "mean concave points", "mean symmetry", "mean fractal dimension"
    ]

    X = df[core_features]
    y = (df["target"] == 0).astype(int)  # 1 = Malignant

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    clf = GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42)
    clf.fit(X_train_s, y_train)

    preds = clf.predict(X_test_s)
    probs = clf.predict_proba(X_test_s)[:, 1]

    metrics = {
        "model_name": "Oncology / Cancer Cytology Screening (GBM)",
        "dataset_samples": len(df),
        "features_count": len(core_features),
        "accuracy": round(float(accuracy_score(y_test, preds)) * 100, 1),
        "roc_auc": round(float(roc_auc_score(y_test, probs)) * 100, 1),
        "precision": round(float(precision_score(y_test, preds)) * 100, 1),
        "recall": round(float(recall_score(y_test, preds)) * 100, 1),
        "feature_importances": sorted(
            [{"feature": f, "importance": round(float(imp) * 100, 2)}
             for f, imp in zip(core_features, clf.feature_importances_)],
            key=lambda x: x["importance"],
            reverse=True
        ),
    }

    joblib.dump({
        "model": clf,
        "scaler": scaler,
        "feature_names": core_features,
        "metrics": metrics,
        "target_mapping": {0: "Benign / Normal Cell Morphology", 1: "Malignant / Atypical Cytology"}
    }, model_path)

    _MODEL_CACHE["cancer"] = joblib.load(model_path)
    return metrics


def _train_heart_model(force: bool = False) -> Dict[str, Any]:
    model_path = MODELS_DIR / "heart_disease_model.joblib"
    if model_path.exists() and not force:
        return joblib.load(model_path)["metrics"]

    csv_path = DATASET_DIR / "heart.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing {csv_path}")

    df = pd.read_csv(csv_path)
    X = df.drop(columns=["target"])
    # In this dataset format, target 0 represents ischemic / occlusion disease findings (high ST depression, occluded vessels, angina)
    y = (df["target"] == 0).astype(int)  # 1 = Heart Disease Detected, 0 = Normal

    feature_names = list(X.columns)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    clf = RandomForestClassifier(n_estimators=150, max_depth=5, random_state=42)
    clf.fit(X_train_s, y_train)

    preds = clf.predict(X_test_s)
    probs = clf.predict_proba(X_test_s)[:, 1]

    metrics = {
        "model_name": "Heart Disease Examination (Cleveland Cardiovascular RF)",
        "dataset_samples": len(df),
        "features_count": len(feature_names),
        "accuracy": round(float(accuracy_score(y_test, preds)) * 100, 1),
        "roc_auc": round(float(roc_auc_score(y_test, probs)) * 100, 1),
        "precision": round(float(precision_score(y_test, preds)) * 100, 1),
        "recall": round(float(recall_score(y_test, preds)) * 100, 1),
        "feature_importances": sorted(
            [{"feature": f, "importance": round(float(imp) * 100, 2)}
             for f, imp in zip(feature_names, clf.feature_importances_)],
            key=lambda x: x["importance"],
            reverse=True
        )[:8],
    }

    joblib.dump({
        "model": clf,
        "scaler": scaler,
        "feature_names": feature_names,
        "metrics": metrics,
        "target_mapping": {0: "Low Cardiac Risk / No Coronary Occlusion", 1: "Elevated Heart Disease Risk (≥50% Stenosis)"}
    }, model_path)

    _MODEL_CACHE["heart"] = joblib.load(model_path)
    return metrics


def _train_diabetes_model(force: bool = False) -> Dict[str, Any]:
    model_path = MODELS_DIR / "diabetes_model.joblib"
    if model_path.exists() and not force:
        return joblib.load(model_path)["metrics"]

    csv_path = DATASET_DIR / "diabetes.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing {csv_path}")

    df = pd.read_csv(csv_path)
    X = df.drop(columns=["Outcome"])
    y = df["Outcome"]

    feature_names = list(X.columns)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    clf = RandomForestClassifier(n_estimators=120, max_depth=5, random_state=42)
    clf.fit(X_train_s, y_train)

    preds = clf.predict(X_test_s)
    probs = clf.predict_proba(X_test_s)[:, 1]

    metrics = {
        "model_name": "Metabolic & Diabetes Examination (Pima Diagnostic RF)",
        "dataset_samples": len(df),
        "features_count": len(feature_names),
        "accuracy": round(float(accuracy_score(y_test, preds)) * 100, 1),
        "roc_auc": round(float(roc_auc_score(y_test, probs)) * 100, 1),
        "precision": round(float(precision_score(y_test, preds)) * 100, 1),
        "recall": round(float(recall_score(y_test, preds)) * 100, 1),
        "feature_importances": sorted(
            [{"feature": f, "importance": round(float(imp) * 100, 2)}
             for f, imp in zip(feature_names, clf.feature_importances_)],
            key=lambda x: x["importance"],
            reverse=True
        ),
    }

    joblib.dump({
        "model": clf,
        "scaler": scaler,
        "feature_names": feature_names,
        "metrics": metrics,
        "target_mapping": {0: "Normal Glucose / Non-Diabetic", 1: "Diabetic / Impaired Glucose Tolerance"}
    }, model_path)

    _MODEL_CACHE["diabetes"] = joblib.load(model_path)
    return metrics


def get_model(model_key: str) -> Dict[str, Any]:
    """Retrieve model bundle from cache or disk; auto-train if not found."""
    if model_key in _MODEL_CACHE:
        return _MODEL_CACHE[model_key]

    path_map = {
        "breast_cancer": MODELS_DIR / "breast_cancer_model.joblib",
        "cancer": MODELS_DIR / "cancer_screening_model.joblib",
        "heart": MODELS_DIR / "heart_disease_model.joblib",
        "diabetes": MODELS_DIR / "diabetes_model.joblib",
    }
    target_path = path_map.get(model_key)
    if target_path and target_path.exists():
        bundle = joblib.load(target_path)
        _MODEL_CACHE[model_key] = bundle
        return bundle

    # Train if missing
    train_and_save_all_models()
    return _MODEL_CACHE.get(model_key, joblib.load(target_path))


def predict_breast_cancer(features: Dict[str, float]) -> Dict[str, Any]:
    """Predict breast cancer malignancy given morphometric features."""
    bundle = get_model("breast_cancer")
    model = bundle["model"]
    scaler = bundle["scaler"]
    feature_names = bundle["feature_names"]

    # Provide fallback median values for missing features if user provided partial features
    csv_path = DATASET_DIR / "breast_cancer.csv"
    df = pd.read_csv(csv_path)
    medians = df.median().to_dict()

    input_vector = []
    for f in feature_names:
        if f in features and features[f] is not None:
            input_vector.append(float(features[f]))
        else:
            input_vector.append(float(medians.get(f, 0.0)))

    X_df = pd.DataFrame([input_vector], columns=feature_names)
    X_scaled = scaler.transform(X_df)

    prob_malignant = float(model.predict_proba(X_scaled)[0, 1])
    is_malignant = prob_malignant >= 0.5
    risk_pct = round(prob_malignant * 100, 1)

    # Compute individual factor contributions based on feature importances and deviation from median
    contributions = []
    for f, val in zip(feature_names, input_vector):
        med = medians.get(f, 1.0)
        std = df[f].std() or 1.0
        z_score = (val - med) / std
        if abs(z_score) > 0.5:
            direction = "elevated" if z_score > 0 else "reduced"
            contributions.append({
                "feature": f,
                "value": round(val, 4),
                "clinical_impact": f"{direction.capitalize()} relative to benign cohort ({abs(round(z_score, 1))} SD)",
                "weight": round(abs(z_score) * 10, 1)
            })

    contributions = sorted(contributions, key=lambda x: x["weight"], reverse=True)[:6]

    if risk_pct >= 75:
        severity = "High / Critical Malignancy Risk"
        recommendation = "Immediate core-needle biopsy referral and histological grading recommended."
    elif risk_pct >= 40:
        severity = "Moderate / Suspicious Lesion"
        recommendation = "Targeted ultrasonography and short-interval mammographic follow-up advised."
    else:
        severity = "Low Risk / Likely Benign"
        recommendation = "Morphology aligns with benign fibroepithelial tissue. Continue routine screening."

    return {
        "examination": "Breast Cancer Examination",
        "predicted_class": "Malignant" if is_malignant else "Benign",
        "is_malignant": is_malignant,
        "risk_percentage": risk_pct,
        "confidence_percentage": round(max(prob_malignant, 1.0 - prob_malignant) * 100, 1),
        "severity": severity,
        "recommendation": recommendation,
        "top_contributing_factors": contributions,
        "model_accuracy": bundle["metrics"]["accuracy"],
        "model_roc_auc": bundle["metrics"]["roc_auc"]
    }


def predict_cancer_screening(features: Dict[str, float]) -> Dict[str, Any]:
    """Predict cytology malignancy risk using the 10 primary cell morphometry features."""
    bundle = get_model("cancer")
    model = bundle["model"]
    scaler = bundle["scaler"]
    feature_names = bundle["feature_names"]

    csv_path = DATASET_DIR / "breast_cancer.csv"
    df = pd.read_csv(csv_path)
    medians = df[feature_names].median().to_dict()

    input_vector = []
    for f in feature_names:
        if f in features and features[f] is not None:
            input_vector.append(float(features[f]))
        else:
            input_vector.append(float(medians.get(f, 0.0)))

    X_df = pd.DataFrame([input_vector], columns=feature_names)
    X_scaled = scaler.transform(X_df)

    prob_malignant = float(model.predict_proba(X_scaled)[0, 1])
    is_malignant = prob_malignant >= 0.5
    risk_pct = round(prob_malignant * 100, 1)

    contributions = []
    for f, val in zip(feature_names, input_vector):
        med = medians.get(f, 1.0)
        std = df[f].std() or 1.0
        z_score = (val - med) / std
        if abs(z_score) > 0.4:
            direction = "atypical increase" if z_score > 0 else "below baseline"
            contributions.append({
                "feature": f,
                "value": round(val, 4),
                "clinical_impact": f"{direction} ({abs(round(z_score, 1))} SD)",
                "weight": round(abs(z_score) * 10, 1)
            })

    contributions = sorted(contributions, key=lambda x: x["weight"], reverse=True)[:5]

    if risk_pct >= 70:
        severity = "High Malignancy Suspicion"
        recommendation = "Oncological consultation and confirmatory surgical pathology required."
    elif risk_pct >= 35:
        severity = "Indeterminate / Borderline Cellular Atypia"
        recommendation = "Repeat fine needle aspirate (FNA) or immunohistochemistry staining recommended."
    else:
        severity = "Benign / Normal Cell Architecture"
        recommendation = "Cytological features consistent with benign cellular growth. Standard observation."

    return {
        "examination": "Cancer Examination & Cytology Screening",
        "predicted_class": "Malignant Pattern" if is_malignant else "Benign Architecture",
        "is_malignant": is_malignant,
        "risk_percentage": risk_pct,
        "confidence_percentage": round(max(prob_malignant, 1.0 - prob_malignant) * 100, 1),
        "severity": severity,
        "recommendation": recommendation,
        "top_contributing_factors": contributions,
        "model_accuracy": bundle["metrics"]["accuracy"],
        "model_roc_auc": bundle["metrics"]["roc_auc"]
    }


def predict_heart_disease(features: Dict[str, float]) -> Dict[str, Any]:
    """Predict coronary artery / heart disease risk using clinical cardiovascular biomarkers."""
    bundle = get_model("heart")
    model = bundle["model"]
    scaler = bundle["scaler"]
    feature_names = bundle["feature_names"]

    csv_path = DATASET_DIR / "heart.csv"
    df = pd.read_csv(csv_path)
    medians = df.median().to_dict()

    input_vector = []
    for f in feature_names:
        if f in features and features[f] is not None:
            input_vector.append(float(features[f]))
        else:
            input_vector.append(float(medians.get(f, 0.0)))

    X_df = pd.DataFrame([input_vector], columns=feature_names)
    X_scaled = scaler.transform(X_df)

    prob_disease = float(model.predict_proba(X_scaled)[0, 1])
    is_positive = prob_disease >= 0.5
    risk_pct = round(prob_disease * 100, 1)

    contributions = []
    readable_labels = {
        "cp": "Chest Pain Type",
        "thalach": "Max Heart Rate",
        "oldpeak": "ST Depression (Oldpeak)",
        "ca": "Major Vessels Colored (Fluoroscopy)",
        "thal": "Thalassemia Scan Defect",
        "trestbps": "Resting Blood Pressure",
        "chol": "Serum Cholesterol",
        "exang": "Exercise Induced Angina",
        "age": "Patient Age",
        "restecg": "Resting ECG Results",
        "slope": "ST Segment Slope"
    }

    for f, val in zip(feature_names, input_vector):
        med = medians.get(f, 0.0)
        std = df[f].std() or 1.0
        z_score = (val - med) / std
        label = readable_labels.get(f, f)
        if abs(z_score) > 0.4:
            contributions.append({
                "feature": label,
                "raw_key": f,
                "value": round(val, 2),
                "clinical_impact": f"{'Higher' if z_score > 0 else 'Lower'} than clinical baseline ({abs(round(z_score, 1))} SD)",
                "weight": round(abs(z_score) * 10, 1)
            })

    contributions = sorted(contributions, key=lambda x: x["weight"], reverse=True)[:6]

    if risk_pct >= 70:
        severity = "High Coronary Risk (>=50% Stenosis)"
        recommendation = "Cardiology referral for stress echocardiogram, troponin review, and coronary angiography."
    elif risk_pct >= 35:
        severity = "Moderate Cardiovascular Risk"
        recommendation = "Holter monitoring, lifestyle intervention, lipid panel optimization, and exercise treadmill test."
    else:
        severity = "Low Cardiac Risk"
        recommendation = "Normal hemodynamic and electrocardiographic profile. Maintain cardiovascular prevention."

    return {
        "examination": "Heart Disease Examination",
        "predicted_class": "Heart Disease Indicated" if is_positive else "Normal Cardiac Profile",
        "has_heart_disease": is_positive,
        "risk_percentage": risk_pct,
        "confidence_percentage": round(max(prob_disease, 1.0 - prob_disease) * 100, 1),
        "severity": severity,
        "recommendation": recommendation,
        "top_contributing_factors": contributions,
        "model_accuracy": bundle["metrics"]["accuracy"],
        "model_roc_auc": bundle["metrics"]["roc_auc"]
    }


def predict_diabetes(features: Dict[str, float]) -> Dict[str, Any]:
    """Predict diabetes / impaired glucose tolerance."""
    bundle = get_model("diabetes")
    model = bundle["model"]
    scaler = bundle["scaler"]
    feature_names = bundle["feature_names"]

    csv_path = DATASET_DIR / "diabetes.csv"
    df = pd.read_csv(csv_path)
    medians = df.median().to_dict()

    input_vector = []
    for f in feature_names:
        if f in features and features[f] is not None:
            input_vector.append(float(features[f]))
        else:
            input_vector.append(float(medians.get(f, 0.0)))

    X_df = pd.DataFrame([input_vector], columns=feature_names)
    X_scaled = scaler.transform(X_df)

    prob_diabetic = float(model.predict_proba(X_scaled)[0, 1])
    is_diabetic = prob_diabetic >= 0.5
    risk_pct = round(prob_diabetic * 100, 1)

    contributions = []
    for f, val in zip(feature_names, input_vector):
        med = medians.get(f, 0.0)
        std = df[f].std() or 1.0
        z_score = (val - med) / std
        if abs(z_score) > 0.4:
            contributions.append({
                "feature": f,
                "value": round(val, 2),
                "clinical_impact": f"{'Elevated' if z_score > 0 else 'Reduced'} relative to normal range",
                "weight": round(abs(z_score) * 10, 1)
            })

    contributions = sorted(contributions, key=lambda x: x["weight"], reverse=True)[:5]

    if risk_pct >= 65:
        severity = "High Diabetic Risk (Type 2 Indication)"
        recommendation = "HbA1c testing, endocrinology consultation, and glycemic management plan."
    elif risk_pct >= 35:
        severity = "Impaired Fasting Glucose / Pre-Diabetic"
        recommendation = "Dietary counseling, physical activity increase, and 3-month fasting glucose retest."
    else:
        severity = "Normal Glycemic Regulation"
        recommendation = "Euglycemic status maintained. Annual wellness metabolic screening advised."

    return {
        "examination": "Diabetes & Metabolic Examination",
        "predicted_class": "Diabetic Profile" if is_diabetic else "Normal Glucose Tolerance",
        "is_diabetic": is_diabetic,
        "risk_percentage": risk_pct,
        "confidence_percentage": round(max(prob_diabetic, 1.0 - prob_diabetic) * 100, 1),
        "severity": severity,
        "recommendation": recommendation,
        "top_contributing_factors": contributions,
        "model_accuracy": bundle["metrics"]["accuracy"],
        "model_roc_auc": bundle["metrics"]["roc_auc"]
    }
