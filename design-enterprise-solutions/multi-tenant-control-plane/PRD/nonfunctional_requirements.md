# Multi-Tenant Control Plane — Non-functional Requirements

## Non-functional requirements

Heavily weighted toward:

- Isolation between tenants
- Safe rollouts (canary, phased)
- Elastic scalability
- Observability
- Disaster recovery
- Backward compatibility across versions

## Service Level Objectives (SLOs)
- **Provisioning Time (p90)**: End-to-end tenant setup (from request to "Ready") < 2 minutes.
- **API Availability**: 99.95% uptime for the Control Plane management APIs.

**Operational considerations:**
- Ensure quotas and metering are robust under scale
- Provide strong tenant isolation (resource, data, and control plane)

> Interviewer focus: separation of control-plane vs data-plane and failure domains.