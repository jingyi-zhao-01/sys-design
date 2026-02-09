# Design Document: Audit Logging System (Phase 2 - Integrity)

**Status:** Draft
**Owner:** @jingyi
**Date:** 2026-02-09

---

## 1. Summary
Phase 2 introduces cryptographic controls to ensure the **immutability** and **tamper-evidence** of the audit trail. By implementing hash-chaining and digital signatures, the system moves from "trusted" to "provable," meeting higher regulatory compliance standards (e.g., SOC2, HIPAA).

---

## 2. Motivation
In Phase 1, the system relied on database permissions to prevent tampering. However, a compromised database administrator or an attacker with high privileges could still alter or delete logs. Phase 2 ensures that any such unauthorized modification is immediately detectable.

---

## 3. Goals
- Implement **Hash Chaining** for the event log.
- Utilize **WORM (Write Once Read Many)** storage for anchoring root hashes.
- Provide **Digital Signatures** to prove the authenticity of the audit trail at specific points in time.
- Create an **Integrity Verifier** tool for automated background checks.

## 4. Non-Goals (Phase 2)
- **High Throughput**: Still limited by synchronous database writes (Phase 3).
- **Public Transparency**: No public blockchain integration; focus is on internal/auditor-facing proof.

---

## 5. Proposed Architecture

### A. Cryptographic Hash Chaining
Every event record now includes a `previous_hash` and a `current_hash`.
- `current_hash = SHA256(JSON_Payload + previous_hash)`
- This creates a continuous chain from the "Genesis Event" to the latest record.
- **Impact**: Deleting a record in the middle of the table breaks all subsequent hashes.

### B. Daily Signing & Anchoring (The Proof)
To prevent an attacker from recalculating the *entire* chain, we must "anchor" the chain root externally.
1. **Daily Signer**: A lambda task triggered every 24 hours.
2. **Action**: It takes the `current_hash` of the last event, signs it using an **AWS KMS** private key, and writes this "Signed Digest" to an immutable **S3 Bucket (Object Lock enabled)**.
3. **WORM Storage**: The S3 Object Lock prevents even the root/admin account from deleting the digest until the retention period (e.g., 7 years) expires.

### C. Integrity Verifier
A background scanner that:
1. Fetches the last Signed Digest from WORM storage.
2. Recursively recalculates hashes from the database records starting from the last verified checkpoint.
3. Verifies that the calculated hash matches the Signed Digest.
4. **Alerting**: If a mismatch is found, it triggers a P0 Security Incident.

---

## 6. Data Model Updates (PostgreSQL)
```sql
ALTER TABLE audit_events 
ADD COLUMN prev_hash BYTEA,
ADD COLUMN event_hash BYTEA NOT NULL;

CREATE INDEX idx_audit_hash_chain ON audit_events(event_hash);
```

---

## 7. Security Considerations
- **KMS Policy**: Only the `DailySigner` service role has `kms:Sign` permissions. The `IntegrityVerifier` only needs `kms:Verify`.
- **Chain of Custody**: By pinning roots to WORM storage, we establish a provable timeline that holds up in legal proceedings.
- **Key Rotation**: KMS keys must be rotated annually; older signatures remain verifiable using the key versioning history.

---

## 8. Success Metrics
- **Verification Pass Rate**: 100% successful daily integrity checks.
- **Detection Time**: Unauthorized deletions detected within < 24 hours (Signer cycle).
- **Compliance Alignment**: Meets "Immutable Audit Trail" requirements for enterprise RFPs.

---

## 9. References & Industry Precedents
- **AWS CloudTrail Log Integrity Validation**: Uses SHA-256 for hashing and RSA for digital signatures to create a tamper-evident log of API calls. [AWS Log Integrity Whitepaper](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html).
- **Oracle Blockchain Tables**: An industry implementation of hash-chaining directly within a relational database to prevent record tampering. [Oracle Blockchain Table Feature](https://docs.oracle.com/en/database/oracle/oracle-database/21/multi/managing-blockchain-tables.html).
- **Apple's Unified Logging**: Emphasizes cryptographic integrity and secure storage of system logs. [Apple Platform Security Guide](https://support.apple.com/guide/security/welcome/web).
