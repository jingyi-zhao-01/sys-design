# Policy & Governance Engine — Non-functional Requirements

## Non-functional requirements

Critical aspects:

- Deterministic evaluation
- Explainability (why allowed/denied)
- High performance
- Backward compatibility
- Tamper resistance
- Traceable history

## Service Level Objectives (SLOs)
- **Evaluation Latency (p95)**: Policy logic execution < 5ms.
- **Distribution Latency**: New/updated policies must reach 100% of enforcement points within < 60 seconds.

**Operational considerations:**
- Provide staging/simulation environments for policy rollout
- Ensure policy changes are auditable and reversible

> Common interview question: “How do you safely roll out a new policy without breaking production?”
