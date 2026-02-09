import pytest
from uuid import uuid4
from src.sdk.client import AuditSDK
from src.common.models.event import Outcome


def test_sdk_sanitization_simple():
    """
    BASIC: Ensure top-level sensitive fields are redacted.
    """
    sdk = AuditSDK(service_id="test-service", ingest_api_url="http://localhost:8000")

    metadata = {
        "user_id": "123",
        "password": "secret_password",
        "token": "sensitive_token",
    }

    # We use a mock or capture the event to check sanitization
    sanitized = sdk._sanitize(metadata)

    assert sanitized["user_id"] == "123"
    assert sanitized["password"] == "[REDACTED]"
    assert sanitized["token"] == "[REDACTED]"


def test_sdk_sanitization_nested():
    """
    INTERMEDIATE: Ensure nested sensitive fields are redacted.
    """
    sdk = AuditSDK(service_id="test-service", ingest_api_url="http://localhost:8000")

    metadata = {
        "request": {
            "headers": {
                "Authorization": "Bearer some-token",
                "Content-Type": "application/json",
            },
            "body": {"credit_card": "1234-5678", "cvv": "123"},
        }
    }

    sanitized = sdk._sanitize(metadata)

    assert sanitized["request"]["headers"]["Authorization"] == "[REDACTED]"
    assert sanitized["request"]["body"]["cvv"] == "[REDACTED]"
    assert sanitized["request"]["headers"]["Content-Type"] == "application/json"


def test_event_model_validation():
    """
    BASIC: Ensure the Pydantic model enforces required fields.
    """
    from src.common.models.event import AuditEvent

    # Missing required actor_id should raise error
    with pytest.raises(ValueError):
        AuditEvent(
            action="login",
            resource_id="res-1",
            outcome=Outcome.SUCCESS,
            service_id="s1",
        )
