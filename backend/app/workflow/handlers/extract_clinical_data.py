"""
Lambda Handler: extractClinicalData
Uses LLM to extract structured clinical data from referral text.
"""

import logging
from typing import Any, Dict

from app.services.llm_service import extract_clinical_data
from app.database.dynamo_mock import llm_outputs_table

logger = logging.getLogger(__name__)


def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input: Referral envelope with referral_text.
    Output: Extracted clinical_data as structured JSON.
    """
    logger.info("extractClinicalData: Extracting clinical info via LLM")

    referral_text = event.get("referral_text", "")
    if not referral_text:
        raise ValueError("referral_text is required for clinical extraction")

    llm_result = extract_clinical_data(referral_text)

    # Store LLM output in DynamoDB mock
    llm_outputs_table.put_item({
        "referral_id": event.get("referral_id"),
        "step": "extractClinicalData",
        "model": llm_result.get("model"),
        "usage": llm_result.get("usage"),
        "raw_response": llm_result.get("raw"),
        "parsed_response": llm_result.get("parsed"),
    })

    return {
        "clinical_data": llm_result["parsed"],
        "extraction_metadata": {
            "model": llm_result.get("model"),
            "usage": llm_result.get("usage"),
        },
        "step": "extractClinicalData",
    }
