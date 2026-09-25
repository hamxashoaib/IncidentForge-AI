from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class IncidentCreate(BaseModel):
    title: str
    service: str
    severity: str = Field(default="P2", pattern="^(P1|P2|P3|P4)$")
    error_rate: float = 0.0
    raw_logs: Optional[str] = None
    metadata_payload: Optional[Dict[str, Any]] = {}

class IncidentResponse(BaseModel):
    id: str
    title: str
    service: str
    severity: str
    status: str
    error_rate: float
    raw_logs: Optional[str]
    metadata_payload: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
