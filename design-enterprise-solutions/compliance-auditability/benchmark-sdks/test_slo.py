import pytest
import time
from src.sdk.client import AuditSDK


# Enterprise SLO Thresholds (Defined in PRD)
SLO_MAX_MEAN_SANITIZATION_MS = 10.0  # Max average time per event sanitization
SLO_MAX_P99_SANITIZATION_MS = 50.0  # Max 99th percentile


def test_slo_sdk_latency_compliance(benchmark):
    """
    SLO TEST: Verifies that the SDK sanitization logic meets the performance targets.
    This test will FAIL if the code changes cause performance to drop below SLOs.
    """
    sdk = AuditSDK()

    # Simulate a typical complex enterprise payload
    complex_payload = {
        "user": {"id": 123, "role": "admin", "token": "secret_token"},
        "action": "UPDATE_USER",
        "metadata": {
            "api_key": "sk_test_12345",
            "request_id": "req_888",
            "nested": {"password": "hashed_stuff", "non_sensitive": "data"},
        },
        "timestamp": time.time(),
    }

    # Run the benchmark
    result = benchmark(sdk._sanitize, complex_payload)

    # Extract stats from pytest-benchmark
    mean_ms = benchmark.stats.stats.mean * 1000
    p99_ms = benchmark.stats.stats.percentile_99 * 1000

    print(
        f"\nSLO Validation: Mean={mean_ms:.3f}ms (Limit: {SLO_MAX_MEAN_SANITIZATION_MS}ms)"
    )
    print(
        f"SLO Validation: P99={p99_ms:.3f}ms (Limit: {SLO_MAX_P99_SANITIZATION_MS}ms)"
    )

    # Assert against SLOs
    assert (
        mean_ms < SLO_MAX_MEAN_SANITIZATION_MS
    ), f"SLO Violation: Mean latency {mean_ms:.3f}ms exceeds limit"
    assert (
        p99_ms < SLO_MAX_P99_SANITIZATION_MS
    ), f"SLO Violation: P99 latency {p99_ms:.3f}ms exceeds limit"


def test_slo_ingestion_throughput_capacity():
    """
    SLO TEST: Simulates a burst of events to verify the client can handle overhead.
    """
    sdk = AuditSDK()
    batch_size = 1000
    start_time = time.perf_counter()

    for _ in range(batch_size):
        sdk._sanitize({"data": "test", "password": "123"})

    total_time = time.perf_counter() - start_time
    events_per_sec = batch_size / total_time

    # Assume an SLO of minimum 5,000 events/sec per SDK instance
    MIN_EVENTS_PER_SEC = 5000
    print(
        f"\nThroughput: {events_per_sec:.2f} events/sec (Min Required: {MIN_EVENTS_PER_SEC})"
    )

    assert (
        events_per_sec > MIN_EVENTS_PER_SEC
    ), f"SLO Violation: Throughput {events_per_sec:.2f} inadequate"
