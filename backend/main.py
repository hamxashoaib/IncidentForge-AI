from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.core.database import engine, Base
from backend.api.routes_incidents import router as incident_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables in PostgreSQL on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="IncidentForge AI Engine",
    description="Autonomous SRE Incident Investigation & Sandbox Validation Engine",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(incident_router)

@app.get("/health")
async def health_check():
    return {"status": "operational", "system": "IncidentForge AI"}
