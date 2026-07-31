"""Persistent audit trail for editor, commit, workspace, and PR analyses."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Float, Integer, JSON, String, Text

from app.core.database import Base


class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    analysis_type = Column(String(50), nullable=False, index=True)
    subject_id = Column(String(500), nullable=False, index=True)
    repository_name = Column(String(255), nullable=True, index=True)
    branch_name = Column(String(255), nullable=True)
    risk_score = Column(Integer, nullable=False, default=0)
    severity = Column(String(50), nullable=False, default="Low")
    decision = Column(String(50), nullable=False, default="ALLOW")
    confidence = Column(Float, nullable=False, default=0.0)
    findings = Column(JSON, nullable=False, default=list)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
