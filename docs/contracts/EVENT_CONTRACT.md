# Event Contract

## 1. Domain Events

All domain events share a common envelope:

```yaml
DomainEvent:
  event_id: string (UUID v7, immutable)
  event_type: string (immutable)
  aggregate_id: string (immutable)
  aggregate_type: string (immutable)
  timestamp: timestamp (immutable)
  data: object (event-specific)
  metadata: EventMetadata
  trace: TraceContext
```

### EventMetadata

```yaml
EventMetadata:
  version: string (semver, immutable)
  source: string (immutable)
  correlation_id: string | null (immutable)
  causation_id: string | null (immutable)
```

## 2. Event Catalog

| Event Type | Aggregate | Description |
|------------|-----------|-------------|
| JobCreated | PrintJob | A new print job was accepted. |
| JobStateChanged | PrintJob | A print job transitioned state. |
| JobCompleted | PrintJob | A print job reached a terminal success state. |
| JobFailed | PrintJob | A print job reached a terminal failure state. |
| JobCancelled | PrintJob | A print job was cancelled. |
| JobRetried | PrintJob | A print job retry was initiated. |
| PrinterRegistered | Printer | A new printer was registered. |
| PrinterStatusChanged | Printer | A printer changed status or health. |
| PrinterObservationReceived | Printer | An observation was received for a printer. |
| ExecutionStarted | PrintExecution | An execution started. |
| ExecutionCompleted | PrintExecution | An execution completed. |
| ExecutionFailed | PrintExecution | An execution failed. |
| ExecutionCancelled | PrintExecution | An execution was cancelled. |
| ProviderRegistered | Provider | A new provider was registered. |
| ProviderStatusChanged | Provider | A provider changed status. |
| DocumentStored | DocumentReference | A document was stored in the spool. |
| DocumentRetrieved | DocumentReference | A document was retrieved from the spool. |
| DocumentDeleted | DocumentReference | A document was garbage collected. |
| StateReconciliation | Printer | Observed state differed from authoritative state. |
| CapabilityMismatch | Printer | Observed capabilities differed from declared capabilities. |
| SpoolError | Spool | A spool I/O error occurred. |
| PolicyViolation | Policy | A policy rule was violated. |

## 3. Event Immutability

- Events are immutable once emitted.
- Events must be stored durably (see SPOOL_CONTRACT.md).
- Events must be ordered by `timestamp` within each aggregate.
- Events must not be modified or deleted after emission.

## 4. Event Versioning

- `metadata.version` identifies the schema version of the event.
- Event schemas are versioned using semantic versioning.
- Consumers must handle unknown event versions gracefully (skip or log).
- Breaking schema changes require a new `event_type` or major version bump.

## 5. Event Delivery

- Events must be delivered to registered subscribers in order.
- Delivery must be at-least-once.
- Subscribers must be idempotent with respect to `event_id`.
- Failed deliveries must be retried with exponential backoff.
- Dead-letter queues must be supported for undeliverable events.

## 6. Event Filtering

- Subscribers may filter events by:
  - `aggregate_type`
  - `aggregate_id`
  - `event_type`
  - Time range
- Filters must be applied at the source to reduce network traffic.

## 7. Correlation and Causation

- `correlation_id` links events that are part of the same logical operation (e.g., a print job and all its executions).
- `causation_id` links events where one caused another (e.g., `JobStateChanged` caused by `ExecutionCompleted`).
- All events generated from an API request must inherit the request's `trace_id`.

## 8. Observability

- Events must be emitted within 100ms of the triggering state change.
- Event emission must not block the triggering operation.
- Failed event emission must not cause the triggering operation to fail (async with retry).
