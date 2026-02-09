# Identity & Access Plane — Non-functional Requirements

**Emphasis:** security, availability, performance and auditability.

## Non-functional requirements

Expect strong emphasis on:

- Very high availability (auth failure = global outage)
- Low latency (often inline in request path)
- Strong consistency for revocation
- Audit integrity
- Security hardening & cryptographic hygiene
- Horizontal scalability
- Multi-region survivability

**Operational considerations:**
- Plan for IdP failure modes and graceful degradation
- Minimize blast radius of stale permissions
- Ensure logs are tamper-evident and retained per policy

> Interviewer prompts: “What happens if the IdP is down?” and “What is the blast radius of a stale permission?”
