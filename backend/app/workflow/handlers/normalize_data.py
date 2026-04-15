"""
Lambda Handler: normalizeData
Cleans and standardizes extracted clinical data for downstream processing.
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

VALID_MOBILITY = {"independent", "assisted", "wheelchair", "bedbound"}
VALID_COGNITIVE = {"intact", "mild_impairment", "moderate_impairment", "severe_impairment"}


def _normalize_list(val: Any) -> List[str]:
    if isinstance(val, list):
        return [str(v).strip().lower() for v in val if v]
    if isinstance(val, str):
        return [v.strip().lower() for v in val.split(",") if v.strip()]
    return []


def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input: Event with clinical_data from extraction step.
    Output: Normalized clinical_data with standardized fields.
    """
    logger.info("normalizeData: Normalizing extracted clinical data")

    clinical = event.get("clinical_data", {})
    if not clinical:
        raise ValueError("clinical_data is required for normalization")

    # Normalize mobility
    mobility = str(clinical.get("mobility", "")).lower().strip()
    if mobility not in VALID_MOBILITY:
        mobility = "assisted"  # safe default

    # Normalize cognitive status
    cognitive = str(clinical.get("cognitive_status", "")).lower().strip().replace(" ", "_")
    if cognitive not in VALID_COGNITIVE:
        cognitive = "intact"

    # Normalize boolean
    oxygen = bool(clinical.get("oxygen_required", False))

    # Normalize lists
    comorbidities = _normalize_list(clinical.get("comorbidities", []))
    key_risks = _normalize_list(clinical.get("key_risks", []))
    medications = _normalize_list(clinical.get("medications", []))
    allergies = _normalize_list(clinical.get("allergies", []))

    # Normalize age
    age = clinical.get("age")
    if age is not None:
        try:
            age = int(age)
        except (ValueError, TypeError):
            age = None

    normalized = {
        "diagnosis": str(clinical.get("diagnosis", "")).strip() or "Unknown",
        "mobility": mobility,
        "comorbidities": comorbidities,
        "oxygen_required": oxygen,
        "cognitive_status": cognitive,
        "key_risks": key_risks,
        "medications": medications,
        "allergies": allergies,
        "age": age,
    }

    return {
        "clinical_data": normalized,
        "normalization_applied": True,
        "step": "normalizeData",
    }
