"""
Multi-Disease Risk Engine (Module 2) + Explainability (Module 3)
====================================================================
For the capstone demo this uses transparent, clinically-referenced rule
thresholds (documented inline) rather than a trained model, so the whole
pipeline runs without needing MIMIC-III access or GPU training up front.
Swap `score_*` functions for real XGBoost/Random Forest inference once
DS2 has trained models — the output shape (risk %, severity, top factors)
stays the same, so nothing downstream (agents, dashboard, care-plan draft)
needs to change.

Each score_* function returns (risk_pct, [ (factor_label, contribution) ])
so the "contribution" list can be rendered exactly like a SHAP force plot
on the frontend.
"""

from __future__ import annotations


def score_heart_risk(systolic_bp, cholesterol, heart_rate, age) -> tuple[float, list[tuple[str, float]]]:
    score, factors = 0.0, []

    if systolic_bp:
        if systolic_bp >= 140:
            score += 30; factors.append(("Systolic BP ≥ 140 mmHg", 30))
        elif systolic_bp >= 130:
            score += 15; factors.append(("Systolic BP 130-139 mmHg", 15))

    if cholesterol:
        if cholesterol >= 240:
            score += 25; factors.append(("Cholesterol ≥ 240 mg/dL", 25))
        elif cholesterol >= 200:
            score += 12; factors.append(("Cholesterol 200-239 mg/dL", 12))

    if heart_rate and heart_rate > 100:
        score += 10; factors.append(("Resting heart rate > 100 bpm", 10))

    if age and age > 55:
        score += 15; factors.append(("Age > 55", 15))

    return min(score, 100.0), factors


def score_diabetes_risk(fasting_glucose, bmi) -> tuple[float, list[tuple[str, float]]]:
    score, factors = 0.0, []

    if fasting_glucose:
        if fasting_glucose >= 126:
            score += 40; factors.append(("Fasting glucose ≥ 126 mg/dL", 40))
        elif fasting_glucose >= 100:
            score += 18; factors.append(("Fasting glucose 100-125 mg/dL (pre-diabetic range)", 18))

    if bmi:
        if bmi >= 30:
            score += 25; factors.append(("BMI ≥ 30 (obese range)", 25))
        elif bmi >= 25:
            score += 10; factors.append(("BMI 25-29.9 (overweight range)", 10))

    return min(score, 100.0), factors


def score_ckd_risk(serum_creatinine, systolic_bp, diabetes_risk_pct) -> tuple[float, list[tuple[str, float]]]:
    score, factors = 0.0, []

    if serum_creatinine:
        if serum_creatinine >= 1.5:
            score += 35; factors.append(("Serum creatinine ≥ 1.5 mg/dL", 35))
        elif serum_creatinine >= 1.2:
            score += 15; factors.append(("Serum creatinine 1.2-1.4 mg/dL", 15))

    if systolic_bp and systolic_bp >= 140:
        score += 15; factors.append(("Elevated systolic BP", 15))

    if diabetes_risk_pct and diabetes_risk_pct >= 50:
        score += 15; factors.append(("Elevated diabetes risk (comorbidity)", 15))

    return min(score, 100.0), factors


def severity_from_score(score: float) -> str:
    if score >= 60:
        return "High"
    if score >= 30:
        return "Moderate"
    return "Low"


def run_multi_disease_assessment(
    age: int | None,
    systolic_bp: float | None,
    diastolic_bp: float | None,
    heart_rate: float | None,
    fasting_glucose: float | None,
    cholesterol: float | None,
    serum_creatinine: float | None,
    bmi: float | None,
) -> dict:
    heart_pct, heart_factors = score_heart_risk(systolic_bp, cholesterol, heart_rate, age)
    diabetes_pct, diabetes_factors = score_diabetes_risk(fasting_glucose, bmi)
    ckd_pct, ckd_factors = score_ckd_risk(serum_creatinine, systolic_bp, diabetes_pct)

    overall_score = round((heart_pct + diabetes_pct + ckd_pct) / 3, 1)

    all_factors = sorted(
        heart_factors + diabetes_factors + ckd_factors, key=lambda f: f[1], reverse=True
    )[:5]

    return {
        "overall_risk_score": overall_score,
        "overall_severity": severity_from_score(overall_score),
        "heart_risk_pct": round(heart_pct, 1),
        "diabetes_risk_pct": round(diabetes_pct, 1),
        "ckd_risk_pct": round(ckd_pct, 1),
        "shap_explanation": {
            "top_factors": [{"factor": f, "contribution": c} for f, c in all_factors],
            "heart_factors": [{"factor": f, "contribution": c} for f, c in heart_factors],
            "diabetes_factors": [{"factor": f, "contribution": c} for f, c in diabetes_factors],
            "ckd_factors": [{"factor": f, "contribution": c} for f, c in ckd_factors],
        },
    }
