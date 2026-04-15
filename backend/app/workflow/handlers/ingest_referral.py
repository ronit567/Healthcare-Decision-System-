"""
Lambda Handler: ingestReferral
Accepts raw referral input and validates/normalizes the initial structure.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

logger = logging.getLogger(__name__)


def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input: Raw referral submission (text or structured JSON).
    Output: Standardized referral envelope ready for pipeline.
    """
    logger.info("ingestReferral: Processing incoming referral")

    referral_text = event.get("referral_text", "")
    patient_name = event.get("patient_name", "Unknown Patient")
    patient_dob = event.get("patient_dob")
    patient_gender = event.get("patient_gender")
    source_facility = event.get("source_facility", "Unknown Facility")
    insurance_provider = event.get("insurance_provider")
    insurance_id = event.get("insurance_id")

    if not referral_text:
        raise ValueError("referral_text is required")

    referral_id = event.get("referral_id", str(uuid.uuid4()))
    patient_id = event.get("patient_id", str(uuid.uuid4()))

    return {
        "referral_id": referral_id,
        "patient_id": patient_id,
        "patient_name": patient_name,
        "patient_dob": patient_dob,
        "patient_gender": patient_gender,
        "source_facility": source_facility,
        "referral_text": referral_text,
        "insurance_provider": insurance_provider,
        "insurance_id": insurance_id,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "step": "ingestReferral",
    }
