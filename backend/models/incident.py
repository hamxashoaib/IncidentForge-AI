from sqlalchemy import Column, String, Float, DateTime, Text, JSON
from sqlalchemy.sql import func
from backend.core.database import Base

class IncidentModel(Base):
    __tablename__ = "incidents"

    id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    service = Column(String(64), nullable=False, index=True)
    severity = Column(String(16), nullable=False) # P1, P2, P3, P4
    status = Column(String(32), default="INVESTIGATING", index=True)
    error_rate = Column(Float, default=0.0)
    raw_logs = Column(Text, nullable=True)
    metadata_payload = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class EvidenceModel(Base):
    __tablename__ = "evidence_ledger"

    id = Column(String(64), primary_key=True, index=True)
    incident_id = Column(String(64), index=True, nullable=False)
    source_type = Column(String(32), nullable=False) # log, metric, git, runbook
    source_ref = Column(String(255), nullable=False)
    payload = Column(Text, nullable=False)
    relevance = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
