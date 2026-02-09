from fastapi import FastAPI, Depends, Request
from src.common.models.event import AuditEvent
from src.service.db.repository import AuditRepository

app = FastAPI(title="Audit Ingest API - Phase 1")


# Dependency injection for DB repository
def get_repo():
    return AuditRepository()


@app.post("/v1/events", status_code=201)
async def ingest_event(event: AuditEvent, repo: AuditRepository = Depends(get_repo)):
    """
    Main endpoint for Phase 1 Ingest.
    """
    await repo.save_event(event)
    return {"status": "accepted", "event_id": event.event_id}


@app.get("/v1/events/search")
async def search_events(actor_id: str, repo: AuditRepository = Depends(get_repo)):
    """
    Basic Search API for Security Observers.
    """
    return await repo.find_by_actor(actor_id)
