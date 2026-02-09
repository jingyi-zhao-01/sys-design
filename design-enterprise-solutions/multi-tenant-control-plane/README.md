# Multi-Tenant Control Plane (Mini Design Practice)

Design a miniature control plane that provisions, configures, and operates a multi-tenant SaaS safely across many customers/orgs.

## What you’re building

A **Tenant Control Plane** that manages tenant lifecycle and configuration, while keeping the **data plane** isolated and scalable.

### MVP scope

- **Tenant model**: orgs/projects, environments (dev/stage/prod), ownership & admin roles
- **Provisioning**: create tenant, allocate resources, set defaults, deprovision/cleanup
- **Configuration**: per-tenant settings, secrets references, region selection
- **Quotas & metering**: basic usage accounting and rate/limit enforcement hooks
- **Rollouts**: feature flags, canary/phased rollout per tenant or cohort
- **Ops hooks**: incident coordination fields (status, maintenance windows), break-glass access workflow
- **Observability**: per-tenant metrics/log tags; ability to answer “which tenants are impacted?”

### Non-goals (for the mini version)

- Full billing/invoicing pipeline
- Full self-serve UI (you can model it as APIs + CLI)
- Complex placement optimization (start with a simple rule-based scheduler)

## Classic reference products

- **AWS Control Tower** (AWS, hyperscaler) — helps set up and govern a multi-account AWS environment with guardrails and account lifecycle.
  - https://aws.amazon.com/controltower/
  - https://docs.aws.amazon.com/controltower/latest/userguide/what-is-control-tower.html

- **Salesforce Platform** (non-hyperscaler) — canonical multi-tenant SaaS platform with strong tenant isolation, governance, and operational controls.
  - https://www.salesforce.com/platform/
  - https://architect.salesforce.com/

## Suggested design questions (practice prompts)

1. What is the **control plane vs data plane** split in your system?
2. What isolation guarantees exist between tenants (compute, storage, config, noisy neighbors)?
3. How do you do safe rollouts (tenant cohorts, canary, rollback, feature compatibility)?
4. What is your blast radius strategy (per-tenant limits, circuit breakers, bulkhead patterns)?
5. How do you manage upgrades when tenants run different versions/configurations?
6. How do you implement quotas/metering so it’s accurate and resilient to retries?
7. What’s your DR plan (RPO/RTO) for control plane state?

## Deliverables (keep it small)

- A short PRD-like statement: goals, users, risks, success metrics
- APIs: create tenant, update config, set quota, rollout flag, deprovision tenant
- Data model: tenants, projects, entitlements, quotas, feature flags, rollout state
- Failure modes: partial provisioning, stuck rollouts, inconsistent config, region outages
- SLOs: provisioning latency, control-plane availability, config propagation time
