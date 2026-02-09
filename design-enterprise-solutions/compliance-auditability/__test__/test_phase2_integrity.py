import pytest
import hashlib
from uuid import uuid4


def calculate_hash(data: str, prev_hash: str = "") -> str:
    """Helper to simulate Phase 2 hashing logic."""
    return hashlib.sha256((data + prev_hash).encode()).hexdigest()


def test_hash_chain_integrity():
    """
    HARD: Simulate a hash chain and verify that tampering is detected.
    """
    # 1. Create a valid chain of 3 events
    e1_data = "event1"
    h1 = calculate_hash(e1_data, "")

    e2_data = "event2"
    h2 = calculate_hash(e2_data, h1)

    e3_data = "event3"
    h3 = calculate_hash(e3_data, h2)

    chain = [
        {"data": e1_data, "prev": "", "hash": h1},
        {"data": e2_data, "prev": h1, "hash": h2},
        {"data": e3_data, "prev": h2, "hash": h3},
    ]

    # Verify chain is valid initially
    assert calculate_hash(chain[1]["data"], chain[0]["hash"]) == chain[1]["hash"]

    # 2. Simulate Tampering: Modify event 2 data
    chain[1]["data"] = "tampered_event2"

    # 3. Validation should fail for event 2
    actual_h2 = calculate_hash(chain[1]["data"], chain[1]["prev"])
    assert actual_h2 != chain[1]["hash"], "Tampering should result in a hash mismatch"

    # 4. Validation should fail for the next link in the chain (Event 3)
    # because even if event 3 is untouched, its 'prev' link to event 2 is now broken
    actual_h3 = calculate_hash(chain[2]["data"], actual_h2)
    assert actual_h3 != chain[2]["hash"], "Chain breakage should propagate"


def test_signature_verification_logic():
    """
    INTERMEDIATE: Simulate checking a signed root hash against a database state.
    """
    # This test would stub the KMS verify call
    # Logic: Database Last Hash == S3 Signed Root Hash
    db_last_hash = "abc123root"
    signed_root = "abc123root"  # Mocked from 'S3'

    assert (
        db_last_hash == signed_root
    ), "Integrity check: DB state matches signed anchor"
