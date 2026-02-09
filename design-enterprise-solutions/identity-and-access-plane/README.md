# Identity & Access Plane (Mini Design Practice)

Design a miniature identity and access solution that turns an unauthenticated request into an **authenticated principal** and an **authorized action**, with strong auditability.

## What you’re building

An **AuthN/AuthZ Service** for a SaaS API that supports end users and machine clients, and exposes a fast authorization check used inline on every request.

### MVP scope

- **AuthN (Users)**: SSO login (OIDC), optional MFA
- **AuthN (Machines)**: API keys or short-lived tokens (service-to-service)
- **Sessions/Tokens**: issue, refresh/rotate, revoke
- **AuthZ**: roles + permissions; `can(actor, action, resource)` evaluation API
- **Directory sync (optional)**: ingest groups from an external IdP/SCIM feed
- **Audit**: log security-relevant events (login, token issuance, role changes, denials)

### Non-goals (for the mini version)

- Full ABAC/ReBAC policy engine (keep it RBAC-first)
- Complex admin UX for access reviews
- Advanced fraud/risk scoring

## Classic reference product

- **Okta** — provides identity management (SSO, MFA, lifecycle) for users and apps.
	- https://www.okta.com/
	- https://developer.okta.com/docs/concepts/oidc/

- **AWS IAM / STS** — defines identities, roles, and policies for AWS resources and issues short-lived credentials for workloads.
	- https://aws.amazon.com/iam/
	- https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html
	- https://docs.aws.amazon.com/STS/latest/APIReference/welcome.html

## Suggested design questions (practice prompts)

1. How do you handle IdP downtime (graceful degradation vs hard fail)?
2. How do you ensure **revocation** takes effect quickly and consistently?
3. Where do you draw the boundary between **authentication** and **authorization** services?
4. How do you avoid turning AuthZ into a latency bottleneck?
5. How do you represent permissions (role-permission table, resource scoping, tenancy)?

## Deliverables (keep it small)

- A short PRD-like statement: goals, users, risks, success metrics
- API sketch: login/token endpoints + `authorize()` endpoint
- Data model sketch: users, roles, role bindings, tokens/sessions
- Threat model: credential theft, replay, confused deputy, privilege escalation
- SLOs: auth latency, availability, revocation propagation time
