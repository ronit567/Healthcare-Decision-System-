import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.postgres import Base


def utcnow():
    return datetime.now(timezone.utc)


class Patient(Base):
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    date_of_birth = Column(String(20), nullable=True)
    gender = Column(String(20), nullable=True)
    insurance_provider = Column(String(255), nullable=True)
    insurance_id = Column(String(100), nullable=True)
    contact_phone = Column(String(30), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    referrals = relationship("Referral", back_populates="patient")


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    source_facility = Column(String(255), nullable=True)
    referral_text = Column(Text, nullable=False)
    referral_data = Column(JSON, nullable=True)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    patient = relationship("Patient", back_populates="referrals")
    decision = relationship("Decision", back_populates="referral", uselist=False)
    workflow_run = relationship("WorkflowRun", back_populates="referral", uselist=False)


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referral_id = Column(UUID(as_uuid=True), ForeignKey("referrals.id"), nullable=False, unique=True)
    decision = Column(String(20), nullable=False)  # ACCEPT, REJECT, REVIEW
    risk_level = Column(String(20), nullable=True)
    risk_score = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    explanation = Column(Text, nullable=True)
    clinical_data = Column(JSON, nullable=True)
    insurance_status = Column(JSON, nullable=True)
    rules_output = Column(JSON, nullable=True)
    llm_reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    referral = relationship("Referral", back_populates="decision")


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referral_id = Column(UUID(as_uuid=True), ForeignKey("referrals.id"), nullable=False, unique=True)
    status = Column(String(50), default="running")  # running, completed, failed
    current_step = Column(String(100), nullable=True)
    started_at = Column(DateTime(timezone=True), default=utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error = Column(Text, nullable=True)

    referral = relationship("Referral", back_populates="workflow_run")
