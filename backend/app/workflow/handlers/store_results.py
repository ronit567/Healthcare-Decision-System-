"""
Lambda Handler: storeResults
Persists final workflow results to PostgreSQL and DynamoDB.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

logger = logging.getLogger(__name__)


def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input: Full pipeline state with all accumulated results.
    Output: Storage confirmation with record IDs.

    Note: Actual DB persistence is handled by the API layer after workflow completes.
    This handler packages the final results for storage.
    """
    logger.info("storeResults: Packaging final results for persistence")

    referral_id = event.get("referral_id")
    patient_id = event.get("patient_id")
    decision_result = event.get("decision_result", {})
    risk_assessment = event.get("risk_assessment", {})
    clinical_data = event.get("clinical_data", {})
    insurance_result = event.get("insurance_result", {})
    rules_output = event.get("rules_output", {})
    llm_reasoning = event.get("llm_reasoning", "")

    final_record = {
        "referral_id": referral_id,
        "patient_id": patient_id,
        "decision": decision_result.get("decision", "REVIEW"),
        "risk_level": risk_assessment.get("risk_level", "medium"),
        "risk_score": risk_assessment.get("confidence", 0.5),
        "confidence": risk_assessment.get("confidence", 0.5),
        "explanation": decision_result.get("explanation", ""),
        "clinical_data": clinical_data,
        "insurance_status": insurance_result,
        "rules_output": rules_output,
        "llm_reasoning": llm_reasoning,
        "key_factors": decision_result.get("key_factors", []),
        "conditions": decision_result.get("conditions", []),
        "urgency": decision_result.get("urgency", "routine"),
        "stored_at": datetime.now(timezone.utc).isoformat(),
        "step": "storeResults",
    }

    return {"final_record": final_record}
