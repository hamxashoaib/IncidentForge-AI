import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.core.database import get_db
from backend.models.incident import IncidentModel
from backend.schemas.incident import IncidentCreate, IncidentResponse

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.post("", response_model=IncidentResponse)
async def create_incident(payload: IncidentCreate, db: AsyncSession = Depends(get_db)):
    incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
    new_incident = IncidentModel(
        id=incident_id,
        title=payload.title,
        service=payload.service,
        severity=payload.severity,
        status="INVESTIGATING",
        error_rate=payload.error_rate,
        raw_logs=payload.raw_logs,
        metadata_payload=payload.metadata_payload or {}
    )
    db.add(new_incident)
    await db.commit()
    await db.refresh(new_incident)
    return new_incident

@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IncidentModel).where(IncidentModel.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return incident
