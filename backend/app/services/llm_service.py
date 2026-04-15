"""
LLM Integration Service — wraps OpenAI API for clinical extraction,
risk scoring, and decision generation. All outputs are strict JSON.
"""

import json
import logging
from typing import Any, Dict

from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


def _call_llm(system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> Dict[str, Any]:
    """Call OpenAI and parse strict JSON response."""
    client = _get_client()
    logger.info("LLM call — system prompt length=%d, user prompt length=%d", len(system_prompt), len(user_prompt))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    logger.debug("LLM raw response: %s", raw)

    parsed = json.loads(raw)
    return {
        "parsed": parsed,
        "raw": raw,
        "model": response.model,
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        },
    }


def extract_clinical_data(referral_text: str) -> Dict[str, Any]:
    """Extract structured clinical data from free-text referral."""
    system_prompt = """You are a clinical data extraction AI. Extract structured medical information from the referral text.
Return ONLY valid JSON with exactly these fields:
{
  "diagnosis": "primary diagnosis string",
  "mobility": "independent|assisted|wheelchair|bedbound",
  "comorbidities": ["list", "of", "comorbidities"],
  "oxygen_required": true/false,
  "cognitive_status": "intact|mild_impairment|moderate_impairment|severe_impairment",
  "key_risks": ["list", "of", "key", "clinical", "risks"],
  "medications": ["list", "of", "current", "medications"],
  "age": number or null,
  "allergies": ["list", "of", "allergies"]
}
If information is not available, use null for strings/numbers, empty arrays for lists, and false for booleans."""

    user_prompt = f"Extract clinical data from this referral:\n\n{referral_text}"

    result = _call_llm(system_prompt, user_prompt)
    return result


def score_risk(clinical_data: Dict[str, Any]) -> Dict[str, Any]:
    """Score patient risk based on extracted clinical data."""
    system_prompt = """You are a clinical risk assessment AI. Analyze the patient clinical data and provide a risk assessment.
Return ONLY valid JSON with exactly these fields:
{
  "risk_level": "low|medium|high",
  "confidence": 0.0 to 1.0,
  "reasoning": "detailed reasoning string",
  "risk_factors": ["list", "of", "contributing", "factors"],
  "recommended_care_level": "routine|elevated|intensive"
}"""

    user_prompt = f"Assess risk for patient with this clinical data:\n\n{json.dumps(clinical_data, indent=2)}"

    result = _call_llm(system_prompt, user_prompt)
    return result


def generate_decision(
    clinical_data: Dict[str, Any],
    risk_assessment: Dict[str, Any],
    insurance_result: Dict[str, Any],
    rules_output: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate final admission decision combining LLM reasoning with rules output."""
    system_prompt = """You are an admission decision AI for a skilled nursing / post-acute care facility.
Given clinical data, risk assessment, insurance status, and rules engine output, generate a final recommendation.

IMPORTANT RULES:
- If rules_output.override_decision is not null, you MUST respect it but explain why.
- If insurance is rejected, recommend REJECT unless clinical urgency overrides.
- Combine your clinical judgment with the deterministic rules.

Return ONLY valid JSON with exactly these fields:
{
  "decision": "ACCEPT|REJECT|REVIEW",
  "explanation": "detailed explanation combining rules and clinical reasoning",
  "key_factors": ["list", "of", "key", "decision", "factors"],
  "conditions": ["any", "conditions", "for", "acceptance"],
  "urgency": "routine|urgent|emergent"
}"""

    user_prompt = f"""Make an admission decision based on:

CLINICAL DATA:
{json.dumps(clinical_data, indent=2)}

RISK ASSESSMENT:
{json.dumps(risk_assessment, indent=2)}

INSURANCE STATUS:
{json.dumps(insurance_result, indent=2)}

RULES ENGINE OUTPUT:
{json.dumps(rules_output, indent=2)}"""

    result = _call_llm(system_prompt, user_prompt, max_tokens=2000)
    return result
