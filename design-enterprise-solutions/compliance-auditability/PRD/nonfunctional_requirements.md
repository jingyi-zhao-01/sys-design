# Compliance & Auditability — Non-functional Requirements

## Non-functional requirements

Here the pressure is on:

- Immutability
- Integrity guarantees
- Long-term durability
- Access controls on logs
- Performance at scale
- Regulatory alignment

## Service Level Objectives (SLOs)
- **Ingestion Latency**: 99% of events must be searchable within < 10 seconds of creation.
- **Storage Durability**: 99.999999999% (11 9s) durability for archived audit logs.

**Operational considerations:**
- Protect logs from tampering; employ immutability and encryption-at-rest
- Plan for long-term retention and legal hold requirements

> Typical question: “How do you ensure logs themselves are not altered by an attacker?”
