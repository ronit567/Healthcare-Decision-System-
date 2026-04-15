"""
Lambda Handler: insuranceCheck
Rule-based insurance verification logic.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Accepted insurance providers
ACCEPTED_PROVIDERS = {
    "medicare", "medicaid", "blue cross", "blue shield", "bluecross",
    "blueshield", "aetna", "cigna", "united healthcare", "unitedhealth",
    "humana", "kaiser", "tricare", "anthem",
}


def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input: Event with insurance_provider and insurance_id.
    Output: insurance_result with verification status.
    """
    logger.info("insuranceCheck: Verifying insurance status")

    provider = (event.get("insurance_provider") or "").strip()
    insurance_id = (event.get("insurance_id") or "").strip()

    has_insurance = bool(provider and insurance_id)

    if not has_insurance:
        return {
            "insurance_result": {
                "has_insurance": False,
                "provider": None,
                "insurance_id": None,
                "verified": False,
                "in_network": False,
                "coverage_level": "none",
                "reason": "No insurance information provided",
            },
            "insurance_data": {"has_insurance": False},
            "step": "insuranceCheck",
        }

    provider_lower = provider.lower()
    in_network = any(accepted in provider_lower for accepted in ACCEPTED_PROVIDERS)

    if in_network:
        coverage_level = "full"
        reason = f"{provider} is an accepted in-network provider"
    else:
        coverage_level = "partial"
        reason = f"{provider} is out-of-network — may require additional authorization"

    return {
        "insurance_result": {
            "has_insurance": True,
            "provider": provider,
            "insurance_id": insurance_id,
            "verified": True,
            "in_network": in_network,
            "coverage_level": coverage_level,
            "reason": reason,
        },
        "insurance_data": {
            "has_insurance": True,
            "in_network": in_network,
            "coverage_level": coverage_level,
        },
        "step": "insuranceCheck",
    }
