from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from backend.core.database import get_db
from backend.models.incident import IncidentModel

router = APIRouter(prefix="/approval", tags=["Human Approval"])

class ApprovalRequest(BaseModel):
    incident_id: str
    decision: str  # "APPROVE" or "REJECT"
    operator_notes: str = ""

@router.post("")
async def process_approval(payload: ApprovalRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IncidentModel).where(IncidentModel.id == payload.incident_id))
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {payload.incident_id} not found")

    if payload.decision.upper() == "APPROVE":
        incident.status = "APPROVED_FOR_DEPLOYMENT"
    elif payload.decision.upper() == "REJECT":
        incident.status = "REJECTED_REINVESTIGATION_REQUIRED"
    else:
        raise HTTPException(status_code=400, detail="Decision must be 'APPROVE' or 'REJECT'")

    metadata = dict(incident.metadata_payload or {})
    metadata["approval_decision"] = payload.decision.upper()
    metadata["operator_notes"] = payload.operator_notes
    incident.metadata_payload = metadata

    await db.commit()
    await db.refresh(incident)

    return {
        "incident_id": incident.id,
        "new_status": incident.status,
        "operator_notes": payload.operator_notes
    }
