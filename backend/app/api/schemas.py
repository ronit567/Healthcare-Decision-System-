"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# --- Request Schemas ---

class ReferralSubmission(BaseModel):
    patient_name: str = Field(..., min_length=1)
    patient_dob: Optional[str] = None
    patient_gender: Optional[str] = None
    source_facility: Optional[str] = "Unknown Facility"
    referral_text: str = Field(..., min_length=10)
    insurance_provider: Optional[str] = None
    insurance_id: Optional[str] = None


# --- Response Schemas ---

class PatientResponse(BaseModel):
    id: str
    name: str
    date_of_birth: Optional[str]
    gender: Optional[str]
    insurance_provider: Optional[str]
    insurance_id: Optional[str]
    created_at: Optional[str]

    class Config:
        from_attributes = True


class DecisionResponse(BaseModel):
    id: str
    referral_id: str
    decision: str
    risk_level: Optional[str]
    risk_score: Optional[float]
    confidence: Optional[float]
    explanation: Optional[str]
    clinical_data: Optional[Dict[str, Any]]
    insurance_status: Optional[Dict[str, Any]]
    rules_output: Optional[Dict[str, Any]]
    llm_reasoning: Optional[str]
    created_at: Optional[str]

    class Config:
        from_attributes = True


class WorkflowRunResponse(BaseModel):
    id: str
    referral_id: str
    status: str
    current_step: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    error: Optional[str]

    class Config:
        from_attributes = True


class ReferralResponse(BaseModel):
    id: str
    patient_id: str
    source_facility: Optional[str]
    referral_text: str
    status: str
    created_at: Optional[str]
    patient: Optional[PatientResponse] = None
    decision: Optional[DecisionResponse] = None
    workflow_run: Optional[WorkflowRunResponse] = None

    class Config:
        from_attributes = True


class WorkflowStepLog(BaseModel):
    step_name: str
    status: str
    input_summary: Optional[str]
    output_summary: Optional[str]
    error: Optional[str]
    duration_ms: Optional[float]
    logged_at: Optional[str]


class PipelineResultResponse(BaseModel):
    workflow_id: str
    status: str
    referral_id: str
    decision: Optional[str]
    execution_log: List[WorkflowStepLog] = []
    message: str
