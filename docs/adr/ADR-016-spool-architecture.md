# ADR-016: Spool Architecture

## Status

Accepted

## Context

PrintForge must store print job documents and metadata durably and efficiently. The spool is the persistent layer for all job-related data.

Requirements:
- Durability: data must survive crashes and power failures.
- Scalability: must handle thousands of concurrent jobs.
- Performance: low-latency reads and writes.
- Flexibility: support multiple storage backends (local filesystem, S3, database).
- Security: encryption at rest, access control.

## Decision

We adopt a pluggable spool architecture with a unified interface:

1. **Spool Interface**: A versioned interface defining `store_document`, `retrieve_document`, `delete_document`, `store_metadata`, `retrieve_metadata`, and `garbage_collect`.
2. **Pluggable Backends**: Multiple backends implement the interface:
   - `LocalFsSpool`: filesystem-based storage for development and small deployments.
   - `S3Spool`: S3-compatible object storage for production.
   - `DatabaseSpool`: relational or document database for structured queries.
3. **Atomicity**: All spool operations are atomic. Partial writes are not allowed.
4. **Encryption**: All data is encrypted at rest. Encryption keys are managed externally.
5. **Indexing**: The spool maintains indexes on `job_id`, `printer_id`, `document_id`, `state`, and `created_at`.
6. **Garbage Collection**: A background process deletes expired jobs and documents based on retention policies.

### Spool Interface

```yaml
Spool:
  store_document(document_id, bytes, format) -> DocumentReference
  retrieve_document(document_id) -> bytes
  delete_document(document_id) -> void
  store_metadata(job) -> void
  retrieve_metadata(job_id) -> PrintJob
  garbage_collect(cutoff_timestamp) -> GCReport
```

### Backend Selection

- Backend is configured via environment or config file.
- The same code path is used regardless of backend.
- Backend-specific optimizations are encapsulated within the implementation.

### Durability Guarantees

- `LocalFsSpool`: uses `fsync` and write-ahead logs.
- `S3Spool`: relies on S3's built-in durability (11 nines).
- `DatabaseSpool`: relies on database write-ahead logging and replication.

## Consequences

### Positive

- Flexible deployment: users choose the backend that fits their environment.
- Consistent API regardless of backend.
- Durability guarantees are enforced uniformly.

### Negative

- Pluggable backends add implementation complexity.
- Performance characteristics vary by backend. The system must handle backend-specific latency.

### Neutral

- This approach is similar to storage abstraction layers in cloud-native systems.
- Future backends (e.g., Azure Blob, GCS) can be added without changing the core.

## References

- SPOOL_CONTRACT.md
- PRINTFORGE_SYSTEM_CONTRACT.md (Deployment Constraints)
