# Design Document: Audit Logging System (Phase 3 - High Throughput & Search)

**Status:** Draft
**Owner:** @jingyi
**Date:** 2026-02-09

---

## 1. Summary
Phase 3 evolves the system to handle **enterprise-scale throughput** and high-performance search capabilities. We decouple the ingestion path from persistence using asynchronity and implement a tiered storage strategy that separates the "Source of Truth" (Compliance) from the "Query Index" (Operations).

---

## 2. Motivation
Phase 2's synchronous database writes create a bottleneck for high-traffic applications and can impact guest latency. Furthermore, relational databases (PostgreSQL) struggle with large-scale full-text search and long-term log retention. Phase 3 introduces architectural patterns used by systems like AWS CloudTrail or GCP Cloud Audit Logs.

---

## 3. Goals
- **Decouple Ingestion**: Move to an asynchronous "Fire and Forget" model for application services.
- **High Ingest Rate**: Support >10,000 events/second.
- **Sub-second Search**: Provide an optimized search index for security investigations.
- **Tiered Storage**: Implement Hot (OpenSearch), Warm (S3), and Cold (Glacier) storage paths.

## 4. Non-Goals (Phase 3)
- **Automatic Remediation**: No automated response to security events (reserved for "Phase 4: Active Defense").
- **External Federation**: Not sharing logs across different organizations.

---

## 5. Proposed Architecture

### A. Asynchronous Streaming (The Buffer)
The Ingest API no longer writes directly to a database.
- **Kafka / Kinesis**: Acts as a high-throughput buffer.
- **Benefit**: If the backend search index or storage is slow or down, the stream buffers the events, preventing data loss and main-app latency spikes.

### B. Polyglot Persistence (Source of Truth vs. Index)
- **Source of Truth (S3 WORM)**:
  - A stream consumer batches events and writes them to S3 in Parquet/JSON format.
  - This path maintains the **Hash Chain** and **Integrity Proofs** from Phase 2.
  - S3 Object Lock ensures regulatory compliance.
- **Search Index (OpenSearch / Elasticsearch)**:
  - A parallel stream consumer indexes events into OpenSearch.
  - **Optimization**: Fields are optimized for full-text search and aggregations (e.g., "Top 10 users by 'Deny' response").

### C. Tiered Retention Logic
1. **Hot (0-30 days)**: Indexed in OpenSearch for immediate investigation.
2. **Warm (31-365 days)**: Stored in S3 Standard; searchable via S3 Select/Athena.
3. **Cold (1-7 years)**: Archived in S3 Glacier for long-term legal/regulatory hold.

---

## 6. Technology Stack
- **Streaming**: Amazon Kinesis or Apache Kafka.
- **Search**: OpenSearch (managed service).
- **Archival**: Amazon S3 with Object Lock.
- **Analytics**: Amazon Athena (for searching across S3 archives without re-indexing).

---

## 7. Operational & Security Considerations
- **Noisy Neighbor**: Implement stream partitioning by `TenantID` to ensure one tenant's audit volume doesn't delay another's.
- **Backpressure**: Monitor stream "Consumer Lag." If the OpenSearch indexer falls behind, ingestion into S3 (the source of truth) must still be prioritized.
- **Index Lifecycle Management (ISM)**: Automate the migration of data from hot indices to archival storage to control OpenSearch costs.

---

## 8. Success Metrics
- **Ingest Latency (SDK Side)**: p99 < 5ms (asynchronous produce call).
- **Consumer Lag**: < 2 seconds from event creation to being searchable in OpenSearch.
- **Search Performance**: Complex queries spanning millions of events return in < 5 seconds.
- **Cost Efficiency**: 70% reduction in per-GB storage cost compared to the Phase 1 relational DB model.

---

## 9. References & Industry Precedents
- **Netflix Keystone**: A real-time stream processing platform that handles trillions of events per day using Kafka as a decoupler. [Netflix Tech Blog: Keystone](https://netflixtechblog.com/keystone-real-time-stream-processing-platform-a3ee651848c0).
- **Uber's ELK Stack**: Implementation of massive-scale log search using OpenSearch/Elasticsearch for real-time operations. [Uber Engineering: Log Search at Scale](https://www.uber.com/en-DE/blog/log-search-at-scale/).
- **AWS CloudTrail Data Plan**: Uses a similar tiered approach (S3 for source of truth, CloudWatch/OpenSearch for hot search, Athena for cold analytics). [AWS CloudTrail Architecture](https://aws.amazon.com/blogs/mt/how-to-use-aws-cloudtrail-to-track-changes-to-your-resources/).
