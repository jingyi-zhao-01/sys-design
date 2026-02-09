# Compliance & Auditability (Mini Design Practice)

Design a miniature compliance/auditability solution that makes actions **provable** to security teams and third parties.

## What you’re building

An **Audit Log Service** that captures security-relevant events, preserves them with integrity guarantees, and supports search/export for investigations and audits.

### MVP scope

- **Ingest**: HTTP API to write audit events (actor, action, resource, timestamp, request id, source IP, outcome)
- **Store**: append-only storage with retention policies and legal hold
- **Query**: search by time range, actor, resource, action, outcome
- **Export**: generate an “evidence package” for a time window (logs + metadata)
- **Access controls**: restrict who can read/export vs write
- **Integrity**: tamper-evident verification (e.g., hash chaining + periodic signed checkpoints)

### Non-goals (for the mini version)

- Full SIEM correlation rules
- Real-time detection/alerting (can be a later iteration)
- Cross-account/org federation

## Classic reference product

- **AWS CloudTrail** — records account activity and API calls to provide a security and compliance audit history.

References:
- https://aws.amazon.com/cloudtrail/
- https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html

## Suggested design questions (practice prompts)

1. What events are *must-log* vs *nice-to-log*?
2. How do you prevent a compromised admin from deleting/modifying audit logs?
3. How do you handle ordering across regions/services?
4. How do you keep query fast without breaking immutability?
5. What are your SLOs (ingest latency, query latency, durability, RPO/RTO)?

## Deliverables (keep it small)

- A short PRD-like statement: goals, users, risks, success metrics
- An API sketch: write event, query events, export evidence
- A storage + integrity approach: how you prove logs weren’t altered
- A minimal threat model: actors, assets, trust boundaries

