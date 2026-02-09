import pytest
import string
import random
from src.sdk.client import AuditSDK


def generate_large_payload(num_keys: int, nesting_depth: int) -> dict:
    """Helper to generate deep nested payloads with potential sensitive data."""
    if nesting_depth == 0:
        return {
            "password": "".join(random.choices(string.ascii_letters, k=20)),
            "api_key": "sk_" + "".join(random.choices(string.digits, k=32)),
            "data": "normal_payload_data",
        }

    return {
        f"node_{i}": generate_large_payload(num_keys, nesting_depth - 1)
        for i in range(num_keys)
    }


def test_sdk_sanitization_performance(benchmark):
    """
    Benchmark the latency of the recursive sanitization logic in the SDK.
    """
    sdk = AuditSDK()
    # Generate a moderately nested payload
    payload = generate_large_payload(num_keys=3, nesting_depth=3)

    # Measure the sanitization process
    result = benchmark(sdk._sanitize, payload)

    assert "password" in str(payload)
    assert "[REDACTED]" in str(result)
