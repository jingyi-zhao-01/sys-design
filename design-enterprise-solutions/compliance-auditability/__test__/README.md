# Compliance Auditability - Testing Guide

This directory contains test suites designed to verify your progress through the different design phases.

## Test Suites

### 1. Phase 1: Functionality ([test_phase1_basics.py](__test__/test_phase1_basics.py))
- **`test_sdk_sanitization_simple`**: Checks if basic fields like `password` are redacted.
- **`test_sdk_sanitization_nested`**: Checks recursive redaction in complex JSON metadata.
- **`test_event_model_validation`**: Ensures the required fields for an enterprise audit event are present.

### 2. Phase 2: Integrity ([test_phase2_integrity.py](__test__/test_phase2_integrity.py))
- **`test_hash_chain_integrity`**: **[Hard]** Simulates a hash chain and verifies that a single bite of tampering in the past breaks the entire subsequent chain.
- **`test_signature_verification_logic`**: Verifies the logic of anchoring a database hash to an immutable signed digest.

### 3. Phase 3: Scale & Search ([test_phase3_scale.py](__test__/test_phase3_scale.py))
- **`test_async_ingestion_latency`**: Ensures the API remains responsive by using asynchronous "Producer" patterns.
- **`test_tiered_storage_routing`**: **[Hard]** Verifies the "Branching" logic where one event must reach both High-Performance Search and High-Durability Archival storage.

## How to run
Ensure you have `pytest` installed:
```bash
pytest design-enterprise-solutions/compliance-auditability/__test__/
```

Use these tests as a "Definition of Done" for your implementation layers.
