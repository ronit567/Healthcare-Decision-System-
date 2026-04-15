"""
Lambda Handler: generateDecision
Combines LLM reasoning with rules engine output to produce final admission decision.
"""

import logging
from typing import Any, Dict

from app.services.llm_service import generate_decision as llm_generate_decision
from app.services.rules_engine import run_rules_engine
from app.database.dynamo_mock import llm_outputs_table

logger = logging.getLogger(__name__)


def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input: Event with clinical_data, risk_assessment, insurance_result.
    Output: Final decision (ACCEPT/REJECT/REVIEW) with explanation.
    """
    logger.info("generateDecision: Generating admission decision")

    clinical_data = event.get("clinical_data", {})
    risk_assessment = event.get("risk_assessment", {})
    insurance_result = event.get("insurance_result", {})
    insurance_data = event.get("insurance_data", {})

    # Run deterministic rules engine
    rules_input = {
        "clinical_data": clinical_data,
        "risk_assessment": risk_assessment,
        "insurance_data": insurance_data,
    }
    rules_output = run_rules_engine(rules_input)

    # Generate LLM decision
    llm_result = llm_generate_decision(
        clinical_data=clinical_data,
        risk_assessment=risk_assessment,
        insurance_result=insurance_result,
        rules_output=rules_output,
    )

    # Store LLM output
    llm_outputs_table.put_item({
        "referral_id": event.get("referral_id"),
        "step": "generateDecision",
        "model": llm_result.get("model"),
        "usage": llm_result.get("usage"),
        "raw_response": llm_result.get("raw"),
        "parsed_response": llm_result.get("parsed"),
    })

    llm_decision = llm_result["parsed"]

    # If rules engine has an override, it takes precedence
    final_decision = rules_output.get("override_decision") or llm_decision.get("decision", "REVIEW")

    explanation_parts = []
    if rules_output.get("override_decision"):
        triggered = rules_output.get("triggered_rules", [])
        rule_msgs = [r.get("message", "") for r in triggered if r.get("message")]
        explanation_parts.append("RULES ENGINE OVERRIDE: " + "; ".join(rule_msgs))
    explanation_parts.append(llm_decision.get("explanation", ""))

    return {
        "decision_result": {
            "decision": final_decision,
            "explanation": "\n\n".join(explanation_parts),
            "key_factors": llm_decision.get("key_factors", []),
            "conditions": llm_decision.get("conditions", []),
            "urgency": llm_decision.get("urgency", "routine"),
        },
        "rules_output": rules_output,
        "llm_reasoning": llm_decision.get("explanation", ""),
        "step": "generateDecision",
    }
