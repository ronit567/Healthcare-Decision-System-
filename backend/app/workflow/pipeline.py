"""
Pipeline Builder — assembles the full referral processing workflow.
Referral → Extract → Normalize → Risk Score → Insurance Check → Decision → Store
"""

from app.workflow.engine import WorkflowEngine
from app.workflow.handlers.ingest_referral import handler as ingest_handler
from app.workflow.handlers.extract_clinical_data import handler as extract_handler
from app.workflow.handlers.normalize_data import handler as normalize_handler
from app.workflow.handlers.risk_scoring import handler as risk_handler
from app.workflow.handlers.insurance_check import handler as insurance_handler
from app.workflow.handlers.generate_decision import handler as decision_handler
from app.workflow.handlers.store_results import handler as store_handler


def build_referral_pipeline(workflow_id: str = None) -> WorkflowEngine:
    """Build and return the full referral processing pipeline."""
    engine = WorkflowEngine(workflow_id=workflow_id)

    engine.add_step("ingestReferral", ingest_handler)
    engine.add_step("extractClinicalData", extract_handler)
    engine.add_step("normalizeData", normalize_handler)
    engine.add_step("riskScoring", risk_handler)
    engine.add_step("insuranceCheck", insurance_handler)
    engine.add_step("generateDecision", decision_handler)
    engine.add_step("storeResults", store_handler)

    return engine
