"""API routes for the Referral Intake & Decision System."""

import logging
import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database.postgres import get_db
from app.database.models import Patient, Referral, Decision, WorkflowRun
from app.database.dynamo_mock import execution_logs_table, llm_outputs_table, workflow_state_table
from app.workflow.pipeline import build_referral_pipeline
from app.api.schemas import (
    ReferralSubmission,
    ReferralResponse,
    PipelineResultResponse,
    PatientResponse,
    DecisionResponse,
    WorkflowRunResponse,
    WorkflowStepLog,
)

logger = logging.getLogger(__name__)
router = APIRouter()


def _serialize_model(obj, fields):
    """Helper to serialize SQLAlchemy models."""
    result = {}
    for f in fields:
        val = getattr(obj, f, None)
        if isinstance(val, (datetime,)):
            val = val.isoformat()
        elif hasattr(val, "hex"):
            val = str(val)
        result[f] = val
    return result


@router.post("/referrals", response_model=PipelineResultResponse)
def submit_referral(submission: ReferralSubmission, db: Session = Depends(get_db)):
    """Submit a new patient referral and run the full AI pipeline."""
    logger.info("New referral submission for patient: %s", submission.patient_name)

    # Create patient record
    patient = Patient(
        name=submission.patient_name,
        date_of_birth=submission.patient_dob,
        gender=submission.patient_gender,
        insurance_provider=submission.insurance_provider,
        insurance_id=submission.insurance_id,
    )
    db.add(patient)
    db.flush()

    # Create referral record
    referral = Referral(
        patient_id=patient.id,
        source_facility=submission.source_facility,
        referral_text=submission.referral_text,
        referral_data=submission.model_dump(),
        status="processing",
    )
    db.add(referral)
    db.flush()

    # Create workflow run record
    workflow_id = str(uuid.uuid4())
    workflow_run = WorkflowRun(
        id=uuid.UUID(workflow_id),
        referral_id=referral.id,
        status="running",
        current_step="ingestReferral",
    )
    db.add(workflow_run)
    db.commit()

    # Build and execute pipeline
    pipeline = build_referral_pipeline(workflow_id=workflow_id)

    pipeline_input = {
        "referral_id": str(referral.id),
        "patient_id": str(patient.id),
        "patient_name": submission.patient_name,
        "patient_dob": submission.patient_dob,
        "patient_gender": submission.patient_gender,
        "source_facility": submission.source_facility,
        "referral_text": submission.referral_text,
        "insurance_provider": submission.insurance_provider,
        "insurance_id": submission.insurance_id,
    }

    try:
        result = pipeline.execute(pipeline_input)

        if result["status"] == "completed":
            final_record = result.get("final_output", {}).get("final_record", {})

            # Store decision in PostgreSQL
            decision = Decision(
                referral_id=referral.id,
                decision=final_record.get("decision", "REVIEW"),
                risk_level=final_record.get("risk_level"),
                risk_score=final_record.get("risk_score"),
                confidence=final_record.get("confidence"),
                explanation=final_record.get("explanation"),
                clinical_data=final_record.get("clinical_data"),
                insurance_status=final_record.get("insurance_status"),
                rules_output=final_record.get("rules_output"),
                llm_reasoning=final_record.get("llm_reasoning"),
            )
            db.add(decision)

            referral.status = "completed"
            workflow_run.status = "completed"
            workflow_run.completed_at = datetime.now(timezone.utc)
            db.commit()

            exec_log = [
                WorkflowStepLog(
                    step_name=log.get("step_name", ""),
                    status=log.get("status", ""),
                    input_summary=log.get("input_summary"),
                    output_summary=log.get("output_summary"),
                    error=log.get("error"),
                    duration_ms=log.get("duration_ms"),
                    logged_at=log.get("logged_at"),
                )
                for log in result.get("execution_log", [])
            ]

            return PipelineResultResponse(
                workflow_id=workflow_id,
                status="completed",
                referral_id=str(referral.id),
                decision=final_record.get("decision"),
                execution_log=exec_log,
                message="Referral processed successfully",
            )
        else:
            referral.status = "failed"
            workflow_run.status = "failed"
            workflow_run.error = result.get("error", "Unknown error")
            workflow_run.completed_at = datetime.now(timezone.utc)
            db.commit()

            exec_log = [
                WorkflowStepLog(
                    step_name=log.get("step_name", ""),
                    status=log.get("status", ""),
                    input_summary=log.get("input_summary"),
                    output_summary=log.get("output_summary"),
                    error=log.get("error"),
                    duration_ms=log.get("duration_ms"),
                    logged_at=log.get("logged_at"),
                )
                for log in result.get("execution_log", [])
            ]

            return PipelineResultResponse(
                workflow_id=workflow_id,
                status="failed",
                referral_id=str(referral.id),
                decision=None,
                execution_log=exec_log,
                message=f"Pipeline failed at step: {result.get('failed_step')}",
            )

    except Exception as e:
        logger.exception("Pipeline execution error")
        referral.status = "failed"
        workflow_run.status = "failed"
        workflow_run.error = str(e)
        workflow_run.completed_at = datetime.now(timezone.utc)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@router.get("/referrals")
def list_referrals(db: Session = Depends(get_db)):
    """List all referrals with patient and decision info."""
    referrals = (
        db.query(Referral)
        .options(
            joinedload(Referral.patient),
            joinedload(Referral.decision),
            joinedload(Referral.workflow_run),
        )
        .order_by(Referral.created_at.desc())
        .all()
    )

    results = []
    for r in referrals:
        item = _serialize_model(r, ["id", "patient_id", "source_facility", "referral_text", "status", "created_at"])

        if r.patient:
            item["patient"] = _serialize_model(
                r.patient, ["id", "name", "date_of_birth", "gender", "insurance_provider", "insurance_id", "created_at"]
            )

        if r.decision:
            item["decision"] = _serialize_model(
                r.decision,
                ["id", "referral_id", "decision", "risk_level", "risk_score", "confidence",
                 "explanation", "clinical_data", "insurance_status", "rules_output", "llm_reasoning", "created_at"],
            )

        if r.workflow_run:
            item["workflow_run"] = _serialize_model(
                r.workflow_run, ["id", "referral_id", "status", "current_step", "started_at", "completed_at", "error"]
            )

        results.append(item)

    return results


@router.get("/referrals/{referral_id}")
def get_referral(referral_id: str, db: Session = Depends(get_db)):
    """Get a single referral with full details."""
    referral = (
        db.query(Referral)
        .options(
            joinedload(Referral.patient),
            joinedload(Referral.decision),
            joinedload(Referral.workflow_run),
        )
        .filter(Referral.id == referral_id)
        .first()
    )
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")

    item = _serialize_model(referral, ["id", "patient_id", "source_facility", "referral_text", "status", "created_at"])

    if referral.patient:
        item["patient"] = _serialize_model(
            referral.patient, ["id", "name", "date_of_birth", "gender", "insurance_provider", "insurance_id", "created_at"]
        )

    if referral.decision:
        item["decision"] = _serialize_model(
            referral.decision,
            ["id", "referral_id", "decision", "risk_level", "risk_score", "confidence",
             "explanation", "clinical_data", "insurance_status", "rules_output", "llm_reasoning", "created_at"],
        )

    if referral.workflow_run:
        item["workflow_run"] = _serialize_model(
            referral.workflow_run, ["id", "referral_id", "status", "current_step", "started_at", "completed_at", "error"]
        )

    return item


@router.get("/referrals/{referral_id}/workflow")
def get_workflow_logs(referral_id: str):
    """Get step-by-step workflow execution logs from DynamoDB mock."""
    # Find workflow_id from execution logs
    all_logs = execution_logs_table.get_all_items()

    # Filter logs for this referral's workflow
    # First find the workflow_id from workflow_state
    states = workflow_state_table.get_all_items()

    # Also check execution logs that might have the referral_id in input_summary
    workflow_ids = set()
    for log in all_logs:
        if referral_id in str(log.get("input_summary", "")):
            workflow_ids.add(log.get("workflow_id"))

    relevant_logs = [log for log in all_logs if log.get("workflow_id") in workflow_ids]
    relevant_logs.sort(key=lambda x: x.get("logged_at", ""))

    return {
        "referral_id": referral_id,
        "workflow_logs": relevant_logs,
    }


@router.get("/referrals/{referral_id}/llm-outputs")
def get_llm_outputs(referral_id: str):
    """Get all LLM outputs for a specific referral."""
    outputs = llm_outputs_table.get_items_by_key("referral_id", referral_id)
    return {
        "referral_id": referral_id,
        "llm_outputs": outputs,
    }


@router.get("/logs")
def get_all_logs():
    """Get all execution logs (observability endpoint)."""
    logs = execution_logs_table.get_all_items()
    logs.sort(key=lambda x: x.get("logged_at", ""), reverse=True)
    return {"logs": logs, "total": len(logs)}


@router.get("/health")
def health_check():
    return {"status": "healthy", "service": "AI Referral Intake & Decision System"}
