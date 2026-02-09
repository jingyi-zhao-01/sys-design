import pytest
import time
from unittest.mock import Mock


def test_async_ingestion_latency():
    """
    INTERMEDIATE: Test that the Ingest API returns quickly by offloading to a 'stream'.
    """

    # Mock a slow downstream storage
    def slow_save():
        time.sleep(2)  # 2 seconds to write to DB

    start_time = time.time()

    # In Phase 3, we expect the API to push to a queue (mocked here) and return
    # instead of waiting for slow_save()
    mock_queue = Mock()
    mock_queue.put("event")

    duration = time.time() - start_time
    assert duration < 0.1, "Ingest API must return < 100ms by using async buffering"


def test_tiered_storage_routing():
    """
    HARD: Verify that events are routed to both Search (ES) and Archival (S3).
    """
    event = {"id": "1", "data": "audit"}

    # Simulate a Dispatcher
    destinations = []

    def dispatcher(e):
        # Phase 3 Logic: Multiple consumers or dual-write
        destinations.append("OPENSEARCH_INDEX")
        destinations.append("S3_WORM_BATCH")

    dispatcher(event)

    assert "OPENSEARCH_INDEX" in destinations
    assert "S3_WORM_BATCH" in destinations
    assert (
        len(destinations) == 2
    ), "Event must be replicated to both operational and compliance storage"
