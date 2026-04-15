"""
Deterministic Rules Engine for referral decision-making.
These rules run alongside LLM outputs and can override or influence final decisions.
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class Rule:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class OxygenAcuityRule(Rule):
    """oxygen_required = true → high acuity case"""

    def __init__(self):
        super().__init__("oxygen_acuity", "Oxygen requirement indicates high acuity")

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        clinical = data.get("clinical_data", {})
        oxygen = clinical.get("oxygen_required", False)
        if oxygen:
            return {
                "rule": self.name,
                "triggered": True,
                "effect": "high_acuity",
                "message": "Patient requires oxygen — flagged as high acuity case",
                "priority_boost": 2,
            }
        return {"rule": self.name, "triggered": False}


class InsuranceRejectRule(Rule):
    """no insurance → reject"""

    def __init__(self):
        super().__init__("insurance_reject", "No insurance leads to rejection")

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        insurance = data.get("insurance_data", {})
        has_insurance = insurance.get("has_insurance", False)
        if not has_insurance:
            return {
                "rule": self.name,
                "triggered": True,
                "effect": "reject",
                "override_decision": "REJECT",
                "message": "Patient has no insurance — automatic rejection per policy",
            }
        return {"rule": self.name, "triggered": False}


class MobilityPriorityRule(Rule):
    """independent mobility → lower priority"""

    def __init__(self):
        super().__init__("mobility_priority", "Independent mobility reduces priority")

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        clinical = data.get("clinical_data", {})
        mobility = clinical.get("mobility", "").lower()
        if mobility == "independent":
            return {
                "rule": self.name,
                "triggered": True,
                "effect": "lower_priority",
                "message": "Patient has independent mobility — lower admission priority",
                "priority_boost": -1,
            }
        return {"rule": self.name, "triggered": False}


class HighRiskAutoReviewRule(Rule):
    """high risk + high confidence → auto-flag for review"""

    def __init__(self):
        super().__init__("high_risk_review", "High risk patients require clinical review")

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        risk = data.get("risk_assessment", {})
        risk_level = risk.get("risk_level", "").lower()
        confidence = risk.get("confidence", 0)
        if risk_level == "high" and confidence >= 0.7:
            return {
                "rule": self.name,
                "triggered": True,
                "effect": "flag_review",
                "message": "High risk with high confidence — flagged for clinical review",
            }
        return {"rule": self.name, "triggered": False}


class CognitiveImpairmentRule(Rule):
    """Severe cognitive impairment → higher care level needed"""

    def __init__(self):
        super().__init__("cognitive_care", "Severe cognitive impairment requires elevated care")

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        clinical = data.get("clinical_data", {})
        cognitive = clinical.get("cognitive_status", "").lower()
        if cognitive in ("severe_impairment", "moderate_impairment"):
            return {
                "rule": self.name,
                "triggered": True,
                "effect": "elevated_care",
                "message": f"Patient has {cognitive} — elevated care level recommended",
                "priority_boost": 1,
            }
        return {"rule": self.name, "triggered": False}


# Registry of all rules
ALL_RULES: List[Rule] = [
    OxygenAcuityRule(),
    InsuranceRejectRule(),
    MobilityPriorityRule(),
    HighRiskAutoReviewRule(),
    CognitiveImpairmentRule(),
]


def run_rules_engine(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run all deterministic rules against the referral data.
    Returns aggregated results with any override decisions.
    """
    results = []
    triggered_rules = []
    override_decision = None
    total_priority_boost = 0

    for rule in ALL_RULES:
        try:
            result = rule.evaluate(data)
            results.append(result)
            if result.get("triggered"):
                triggered_rules.append(result)
                total_priority_boost += result.get("priority_boost", 0)
                if result.get("override_decision"):
                    override_decision = result["override_decision"]
                    logger.warning("Rule '%s' overrides decision to %s", rule.name, override_decision)
        except Exception as e:
            logger.error("Rule '%s' failed: %s", rule.name, str(e))
            results.append({"rule": rule.name, "triggered": False, "error": str(e)})

    return {
        "all_results": results,
        "triggered_rules": triggered_rules,
        "triggered_count": len(triggered_rules),
        "total_rules": len(ALL_RULES),
        "override_decision": override_decision,
        "priority_adjustment": total_priority_boost,
    }
