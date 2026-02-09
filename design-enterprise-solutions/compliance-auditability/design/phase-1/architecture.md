# Design Document: Audit Logging System (Phase 1)

**Status:** Draft / Approved
**Owner:** @jingyi
**Date:** 2026-02-09

---

## 1. Summary
A primitive, functional audit logging solution providing a standard way for internal services to record security-relevant events. Phase 1 focuses on a synchronous SDK-to-Database path with mandatory data sanitization.

---

## 2. Motivation
Enterprises require tracing "who did what and when." While we eventually need high-scale and tamper-proof logs, Phase 1 establishes the **Standard Event Schema** and **Sanitization SDK** used by all subsequent phases.

---

## 3. Goals
- Provide a standard **Audit SDK** for all application services.
- Ensure **Zero-Credential Logging** via mandatory client-side redaction.
- Persist events in a searchable, relational format.
- Provide a basic **Search API** for security auditors.

## 4. Non-Goals (Phase 1)
- **High Throughput**: Not designed for >500 events/sec (Phase 3).
- **Tamper Evidence**: No hash-chaining or digital signatures (Phase 2).
- **Long-term Archival**: Not handling S3 Glacier or cold storage logic.

---

## 5. Proposed Design

### A. The Audit SDK
The SDK is a wrapper around the Ingest API. It performs **Sanitization** locally before transmission.
- **Mandatory Redaction**: `password`, `secret`, `token`, `authorization_header`, `cvv`.
- **Enrichment**: Automatically attaches `source_ip`, `service_id`, and `trace_id`.

### B. Ingest API
A simple REST/gRPC endpoint.
- **Endpoint**: `POST /v1/events`
- **Behavior**: Validates schema -> Synchronously writes to DB.

### C. Data Model (PostgreSQL)
```sql
CREATE TABLE audit_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    actor_id VARCHAR(255) NOT NULL,
    action VARCHAR(50) NOT NULL,
    resource_id VARCHAR(255) NOT NULL,
    outcome VARCHAR(20) NOT NULL, -- SUCCESS, FAILURE, DENIED
    metadata JSONB, -- Sanitized context
    request_id UUID,
    source_ip INET
);
CREATE INDEX idx_audit_actor_time ON audit_events(actor_id, timestamp DESC);
```

---

## 6. Security & Privacy
- **Redaction**: Services must define a "Sensitive Fields" list that the SDK scrubs.
- **Access Control**: The Search API must be restricted to the `SecurityAuditor` role only.
- **Anonymization**: If logs are exported for analytics, PII (emails/IPs) must be masked.

---

## 7. Alternatives Considered
- **Logging to File/Stdout**: Simple, but requires log-drainer infra (Splunk/ELK) which we aren't assuming yet.
- **NoSQL (DynamoDB)**: Good for scale, but SQL is faster for complex multi-attribute queries in early stages.

---

## 8. Success Metrics
- **SDK Adoption**: % of services using the standard wrapper.
- **Redaction Rate**: 0% sensitive tokens found in production audit scans.
- **Latency**: Ingest overhead < 10ms for calling services.

---

## 9. References & Industry Precedents
- **AWS CloudTrail Schema**: Industry standard for audit event fields (EventTime, EventName, UserIdentity, SourceIPAddress). [AWS CloudTrail Documentation](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html).
- **Google Cloud Audit Logs**: Use of structured JSON logs for attribution and searchability. [GCP Audit Logs Reference](https://cloud.google.com/logging/docs/audit).
- **Stripe API Design**: Known for rigorous request/response sanitization and auditability of developer actions. [Stripe Audit Logs](https://stripe.com/docs/audit-logs).
