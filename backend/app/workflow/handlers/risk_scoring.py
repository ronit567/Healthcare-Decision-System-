"""
Lambda Handler: riskScoring
Uses LLM to assess patient risk based on normalized clinical data.
"""

import logging
from typing import Any, Dict

from app.services.llm_service import score_risk
from app.database.dynamo_mock import llm_outputs_table

logger = logging.getLogger(__name__)


def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input: Event with normalized clinical_data.
    Output: risk_assessment with risk_level, confidence, reasoning.
    """
    logger.info("riskScoring: Scoring patient risk via LLM")

    clinical_data = event.get("clinical_data", {})
    if not clinical_data:
        raise ValueError("clinical_data is required for risk scoring")

    llm_result = score_risk(clinical_data)

    # Store LLM output in DynamoDB mock
    llm_outputs_table.put_item({
        "referral_id": event.get("referral_id"),
        "step": "riskScoring",
        "model": llm_result.get("model"),
        "usage": llm_result.get("usage"),
        "raw_response": llm_result.get("raw"),
        "parsed_response": llm_result.get("parsed"),
    })

    risk = llm_result["parsed"]

    return {
        "risk_assessment": {
            "risk_level": risk.get("risk_level", "medium"),
            "confidence": risk.get("confidence", 0.5),
            "reasoning": risk.get("reasoning", ""),
            "risk_factors": risk.get("risk_factors", []),
            "recommended_care_level": risk.get("recommended_care_level", "routine"),
        },
        "risk_metadata": {
            "model": llm_result.get("model"),
            "usage": llm_result.get("usage"),
        },
        "step": "riskScoring",
    }
