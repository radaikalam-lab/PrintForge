# ADR-017: Persistence Abstraction

## Status

Accepted

## Context

PrintForge must persist various types of data: job metadata, printer state, events, observations, and configuration. Different persistence needs require different storage technologies:
- Job metadata: structured, queryable, transactional.
- Events: append-only, ordered, high-write-throughput.
- Documents: binary, large, durable.
- Configuration: small, low-latency, strongly consistent.

We need a persistence abstraction that provides the right storage for each data type without coupling the core to specific databases.

## Decision

We adopt a persistence abstraction layer with specialized stores:

1. **Job Store**: Relational database (PostgreSQL) for structured job and printer metadata. Supports transactions, joins, and complex queries.
2. **Event Store**: Append-only log (event store or Kafka) for domain events. Supports ordered consumption and replay.
3. **Spool**: Pluggable backend for documents (see ADR-016).
4. **Config Store**: Embedded key-value store (e.g., SQLite, BoltDB) for configuration. Low-latency, strongly consistent.
5. **Cache**: In-memory cache (Redis or in-process) for hot data (printer status, job state).

### Abstraction Interface

Each store exposes a versioned interface:

```yaml
JobStore:
  create_job(job) -> PrintJob
  get_job(job_id) -> PrintJob | null
  update_job(job) -> PrintJob
  list_jobs(filter) -> Page[PrintJob]

EventStore:
  append(event) -> void
  read(aggregate_id, from_timestamp) -> Event[]
  subscribe(filter, handler) -> Subscription

Spool:
  store_document(...) -> DocumentReference
  retrieve_document(...) -> bytes
  ...
```

### Transaction Boundaries

- Job state transitions and event emissions are atomic: either both succeed or both fail.
- Document storage is atomic with job metadata updates.
- Configuration changes are atomic and versioned.

### Consistency Model

- Job Store: strong consistency.
- Event Store: sequential consistency per aggregate.
- Spool: eventual consistency across backends (but atomic within a backend).
- Cache: eventual consistency with Job Store.

## Consequences

### Positive

- Each data type uses the optimal storage technology.
- The core is decoupled from specific databases.
- Different stores can be scaled independently.

### Negative

- Multiple storage technologies increase operational complexity.
- Cross-store transactions are complex and may require sagas or two-phase commit.

### Neutral

- This approach is common in event-sourced systems.
- The abstraction allows swapping implementations (e.g., replace PostgreSQL with CockroachDB).

## References

- SPOOL_CONTRACT.md
- EVENT_CONTRACT.md
- PRINTFORGE_SYSTEM_CONTRACT.md
