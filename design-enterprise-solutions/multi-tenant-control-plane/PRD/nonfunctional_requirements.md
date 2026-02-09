# Multi-Tenant Control Plane — Non-functional Requirements

## Non-functional requirements

Heavily weighted toward:

- Isolation between tenants
- Safe rollouts (canary, phased)
- Elastic scalability
- Observability
- Disaster recovery
- Backward compatibility across versions

**Operational considerations:**
- Ensure quotas and metering are robust under scale
- Provide strong tenant isolation (resource, data, and control plane)

> Interviewer focus: separation of control-plane vs data-plane and failure domains.