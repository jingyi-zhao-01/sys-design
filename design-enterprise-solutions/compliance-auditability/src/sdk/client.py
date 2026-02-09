import logging
import json
from typing import Any, Dict, List
from src.common.models.event import AuditEvent, Outcome


class AuditSDK:
    """
    Client-side SDK for sanitizing and dispatching audit events.
    """

    def __init__(
        self, service_id: str, ingest_api_url: str, sensitive_fields: List[str] = None
    ):
        self.service_id = service_id
        self.ingest_api_url = ingest_api_url
        self.sensitive_fields = sensitive_fields or [
            "password",
            "token",
            "secret",
            "authorization",
            "cvv",
        ]
        self.logger = logging.getLogger(__name__)

    def _sanitize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively redacts sensitive fields defined in the SDK.
        """
        sanitized = {}
        for k, v in data.items():
            if k.lower() in self.sensitive_fields:
                sanitized[k] = "[REDACTED]"
            elif isinstance(v, dict):
                sanitized[k] = self._sanitize(v)
            else:
                sanitized[k] = v
        return sanitized

    def record(
        self,
        actor_id: str,
        action: str,
        resource_id: str,
        outcome: Outcome,
        metadata: Dict[str, Any] = None,
        **kwargs,
    ):
        """
        Entry point for applications to log an event.
        """
        sanitized_metadata = self._sanitize(metadata or {})

        event = AuditEvent(
            actor_id=actor_id,
            action=action,
            resource_id=resource_id,
            outcome=outcome,
            metadata=sanitized_metadata,
            service_id=self.service_id,
            **kwargs,
        )

        self._dispatch(event)

    def _dispatch(self, event: AuditEvent):
        """
        Phase 1: Synchronous dispatch to Ingest API.
        """
        # TODO: Implement HTTP POST call to self.ingest_api_url
        self.logger.info(f"Dispatching audit event: {event.event_id}")
        pass
