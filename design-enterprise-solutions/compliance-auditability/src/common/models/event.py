from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, ConfigDict


class Outcome(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    DENIED = "DENIED"


class AuditEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_id: UUID = uuid4()
    timestamp: datetime = datetime.now()
    actor_id: str
    action: str
    resource_id: str
    outcome: Outcome
    request_id: Optional[UUID] = None
    source_ip: Optional[str] = None
    metadata: Dict[str, Any] = {}
    service_id: str
    trace_id: Optional[str] = None
