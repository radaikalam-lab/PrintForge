# Spool Contract

## 1. Spool Storage Requirements

The spool is the persistent, durable storage for print job documents and metadata.

```yaml
Spool:
  backend: SpoolBackend (pluggable)
  path: string (configurable, immutable per backend)
  encryption: SpoolEncryption (required)
  retention: RetentionPolicy (configurable)
  indexing: SpoolIndex (required)
```

## 2. SpoolBackend Enum

| Value | Description |
|-------|-------------|
| LOCAL_FS | Local filesystem with directory-based storage. |
| S3 | Amazon S3 or compatible object storage. |
| DATABASE | Relational or document database. |
| MEMORY | In-memory backend for testing only. |

## 3. Document Storage

- Documents must be stored in their canonical representation (see DOCUMENT_CONTRACT.md).
- Documents must be immutable once stored.
- Documents must be addressable by `document_ref.document_id`.
- Partial writes are not allowed. A document must be written atomically.

## 4. Encryption

- All documents in the spool must be encrypted at rest.
- Encryption keys must be managed externally (e.g., KMS, vault).
- The spool backend must not expose encryption keys in logs or metrics.

## 5. Retention Policy

```yaml
RetentionPolicy:
  completed_job_ttl: duration (e.g., "720h" = 30 days)
  failed_job_ttl: duration (e.g., "168h" = 7 days)
  archived_job_ttl: duration (e.g., "2160h" = 90 days)
  document_ttl: duration (must be >= job_ttl)
```

- When a job reaches a terminal state, its retention timer starts.
- After TTL expires, the job and its document are eligible for garbage collection.
- Garbage collection must be atomic: either both job metadata and document are deleted, or neither.

## 6. Indexing

- The spool must maintain indexes on:
  - `job_id`
  - `printer_id`
  - `document_id`
  - `state`
  - `created_at`
- Indexes must be updated atomically with data writes.
- Queries by `job_id` must be O(1) or O(log n).

## 7. Durability

- The spool must guarantee durability: once a write is acknowledged, the data must survive process crashes and power failures.
- For filesystem backends, this requires `fsync` or equivalent.
- For database backends, this requires write-ahead logging with synchronous commits.

## 8. Consistency

- The spool is the source of truth for job and document state.
- All reads must return the latest committed state.
- Concurrent writes to the same job must be serialized and handled via optimistic concurrency control (version vector or ETag).

## 9. Spool Events

The spool must emit the following events (see EVENT_CONTRACT.md):
- `DocumentStored` when a document is written.
- `DocumentRetrieved` when a document is read (for audit).
- `DocumentDeleted` when a document is garbage collected.
- `SpoolError` when an I/O error occurs.

## 10. Testing

- The spool must be fully testable with the `MEMORY` backend.
- Integration tests must verify durability and consistency guarantees.
