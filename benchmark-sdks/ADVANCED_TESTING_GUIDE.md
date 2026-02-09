# Advanced Testing Guide: Distributed Scale (k6) & Chaos

This guide focuses on using **Grafana Cloud k6 (Free Tier)** to validate the enterprise scalability of the Compliance & Auditability system.

## 1. Managed Load Testing with Grafana Cloud k6
Instead of managing your own infrastructure, use the Grafana Cloud free tier to run distributed tests from managed infrastructure.

### Configuration (`load-test.js`)
Create a simple k6 script to hit the Ingest API:
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  ext: {
    loadimpact: {
      projectID: 123456, // Your Grafana Cloud Project ID
      name: "Compliance Ingest Test"
    }
  },
  vus: 50, // Free tier limit
  duration: '5m',
};

export default function () {
  const payload = JSON.stringify({
    event: "user_login",
    user_id: "u_99",
    metadata: { password: "redact_me" }
  });
  const res = http.post('https://api.your-enterprise.com/v1/ingest', payload);
  check(res, { 'status is 202': (r) => r.status === 202 });
  sleep(0.1);
}
```

### Execution
1. Install k6: `brew install k6` or download the binary.
2. Login: `k6 login cloud --token <your-grafana-token>`.
3. Run: `k6 run -o cloud load-test.js`.

---

## 2. Infrastructure Requirements (Middleware)
To support Phase 3 testing, ensure the following are reachable by your API:

*   **Kafka**: 1-3 Nodes (Standard Ingestion).
*   **Redis**: For global rate limiting checks.
*   **S3/Object Storage**: To verify long-term archival.

---

## 3. Simple Chaos Scenarios
Use the load test above and manually trigger these "resilience checks":

1.  **Kafka Slowdown**: Limit IOPS on the Kafka drive; verify the Ingest API doesn't hang (Non-blocking SLO).
2.  **Auth Failure**: Revoke the API key used by k6; verify logs still reach the "Security Audit" bucket even for unauthorized attempts.
3.  **Data Tampering**: Manually edit a DB record to verify the Hash-Chain integrity check fails during the next scan.
