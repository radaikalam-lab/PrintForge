# ADR-007: Event Delivery Semantics

## Status

Accepted

## Context

PrintForge uses events for communication between components. The delivery semantics must be explicit and realistic; claiming exactly-once delivery without a mechanism to guarantee it leads to incorrect assumptions in consumers.

## Decision

PrintForge uses **at-least-once delivery** with **idempotent consumers**.

Chosen properties:
- at-least-once delivery
- duplicate handling via event_id idempotency
- replay semantics: events may be replayed from store
- dead-letter behavior: undeliverable events move to dead-letter queue

Event identity:
```text
event_id: UUID v7
schema_version: semver
producer: component identifier
timestamp: ISO-8601
correlation_id: UUID | null
causal_id: UUID | null
ordering_scope: aggregate_id
idempotency_key: event_id
```

Consumers must be idempotent with respect to event_id. Failed deliveries are retried with exponential backoff. Dead-letter queues capture undeliverable events.

## Consequences

### Positive

- At-least-once is achievable and well-understood.
- Idempotent consumers are straightforward to implement.
- Replay is supported naturally.

### Negative

- Consumers must handle duplicates.
- Exactly-once semantics are not available without significant infrastructure.

### Neutral

- This is the standard approach for distributed event systems (e.g., Kafka).
- Dead-letter queues require operational awareness.

## Alternatives Considered

1. **Exactly-once delivery**: Claimed but not guaranteed in practice. Rejected because it creates false confidence.
2. **At-most-once delivery**: Simple but loses events. Rejected because state changes must not disappear.

## References

- EVENT_CONTRACT.md
- FAILURE_CONTRACT.md
