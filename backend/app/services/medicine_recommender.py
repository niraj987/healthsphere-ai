"""
Medicine / Drug-Information Recommendation Service
====================================================

IMPORTANT — SCOPE AND SAFETY BOUNDARY
--------------------------------------
This service does NOT decide dosage and does NOT autonomously prescribe.
It looks up *general drug information* (what a drug class is commonly used
for, known interactions, standard formulations) from public, authoritative
sources and returns it as a candidate list for a licensed doctor to review,
edit, and approve inside a CarePlan. Every record it produces is written
with doctor_status="pending_review" (see models.MedicineRecommendation) and
must be explicitly approved before a patient ever sees it as part of their
care plan.

Data sources (both free, public, no key required for the endpoints used):
  - RxNav / RxNorm (U.S. National Library of Medicine)
      https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html
      Used for: normalizing a drug/condition name to a standard RxNorm
      concept (RxCUI), finding related/class drugs.
  - openFDA Drug Label API (U.S. FDA)
      https://open.fda.gov/apis/drug/label/
      Used for: pulling the "indications_and_usage" and "warnings" sections
      of the official label for a given drug name.

If your capstone grader/team prefers a different source (e.g. a licensed
FDB/First Databank feed, or DrugBank), swap the two `_call_*` functions
below — the rest of the pipeline (normalize -> lookup -> store -> doctor
review) stays the same.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import requests

logger = logging.getLogger("healthsphere.medicine_recommender")

RXNAV_BASE = "https://rxnav.nlm.nih.gov/REST"
OPENFDA_BASE = "https://api.fda.gov/drug/label.json"

# A small, editable map from disease-module outputs to first-line drug
# CLASSES (not specific dosed prescriptions) commonly discussed for that
# condition. This is a starting point for the capstone demo — a real
# deployment should source this table from a licensed clinical formulary
# and have it signed off by a clinician advisor.
CONDITION_TO_DRUG_CLASS: dict[str, list[str]] = {
    "heart_risk": ["statin", "beta blocker", "ACE inhibitor", "aspirin"],
    "diabetes_risk": ["metformin", "SGLT2 inhibitor", "GLP-1 receptor agonist"],
    "ckd_risk": ["ACE inhibitor", "ARB", "phosphate binder"],
}


@dataclass
class DrugCandidate:
    condition: str
    candidate_drug_name: str
    rxnorm_cui: str | None
    drug_class: str
    general_info: str
    interaction_warnings: list[str] = field(default_factory=list)
    source_api: str = "RxNav/RxNorm + openFDA"


def _call_rxnav_search(term: str) -> dict[str, Any]:
    resp = requests.get(
        f"{RXNAV_BASE}/drugs.json",
        params={"name": term},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def _call_openfda_label(drug_name: str) -> dict[str, Any] | None:
    try:
        resp = requests.get(
            OPENFDA_BASE,
            params={"search": f'openfda.brand_name:"{drug_name}"', "limit": 1},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results") or []
        return results[0] if results else None
    except requests.RequestException as exc:
        logger.warning("openFDA lookup failed for %s: %s", drug_name, exc)
        return None


def lookup_drug_class(drug_class_term: str) -> list[DrugCandidate]:
    """Resolve a drug-class term (e.g. 'metformin') to RxNorm concepts + label info."""
    candidates: list[DrugCandidate] = []
    try:
        data = _call_rxnav_search(drug_class_term)
    except requests.RequestException as exc:
        logger.warning("RxNav lookup failed for %s: %s", drug_class_term, exc)
        return candidates

    groups = (data.get("drugGroup") or {}).get("conceptGroup") or []
    for group in groups:
        for concept in (group.get("conceptProperties") or [])[:3]:  # cap results
            name = concept.get("name", drug_class_term)
            cui = concept.get("rxcui")
            label = _call_openfda_label(concept.get("synonym", name).split()[0])
            general_info = (
                " ".join(label.get("indications_and_usage", []))[:600]
                if label
                else f"Commonly discussed within the '{drug_class_term}' class. "
                "No FDA label match found — verify with a clinical formulary."
            )
            warnings = (label.get("warnings", []) if label else []) or []
            candidates.append(
                DrugCandidate(
                    condition=drug_class_term,
                    candidate_drug_name=name,
                    rxnorm_cui=cui,
                    drug_class=drug_class_term,
                    general_info=general_info,
                    interaction_warnings=[w[:300] for w in warnings[:2]],
                )
            )
    return candidates


def recommend_for_risk_profile(
    heart_risk_pct: float | None,
    diabetes_risk_pct: float | None,
    ckd_risk_pct: float | None,
    threshold_pct: float = 50.0,
) -> list[DrugCandidate]:
    """
    Given a patient's disease-risk percentages from Module 2 (ML Engine),
    return candidate drug-class information for every risk above threshold.
    This is the function the Clinician Assist Agent calls before drafting a
    care-plan suggestion — the doctor still approves/edits every item.
    """
    risk_map = {
        "heart_risk": heart_risk_pct,
        "diabetes_risk": diabetes_risk_pct,
        "ckd_risk": ckd_risk_pct,
    }

    all_candidates: list[DrugCandidate] = []
    for condition, pct in risk_map.items():
        if pct is None or pct < threshold_pct:
            continue
        for drug_class_term in CONDITION_TO_DRUG_CLASS.get(condition, []):
            for candidate in lookup_drug_class(drug_class_term):
                candidate.condition = condition
                all_candidates.append(candidate)

    return all_candidates


def to_db_rows(candidates: list[DrugCandidate], patient_id: int, assessment_id: int | None):
    """Convert DrugCandidate dataclasses into MedicineRecommendation ORM rows."""
    from app.models.models import MedicineRecommendation

    return [
        MedicineRecommendation(
            patient_id=patient_id,
            assessment_id=assessment_id,
            condition=c.condition,
            candidate_drug_name=c.candidate_drug_name,
            rxnorm_cui=c.rxnorm_cui,
            drug_class=c.drug_class,
            source_api=c.source_api,
            general_info=c.general_info,
            interaction_warnings=c.interaction_warnings,
            doctor_status="pending_review",
        )
        for c in candidates
    ]
