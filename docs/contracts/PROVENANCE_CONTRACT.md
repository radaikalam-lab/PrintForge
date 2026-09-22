# Provenance Contract

## 1. Provenance Requirement

Every state change, event, and observation in PrintForge must carry an immutable provenance chain.

## 2. TraceContext Object

```yaml
TraceContext:
  trace_id: string (UUID v7)
  span_id: string (UUID v7)
  parent_span_id: string | null
  baggage: map<string, string>
```

### Fields

- **trace_id**: Identifies the entire causal chain. Generated at the entry point (API request or event trigger).
- **span_id**: Identifies the current operation.
- **parent_span_id**: Identifies the parent operation. Null for root spans.
- **baggage**: Key-value pairs propagated across service boundaries.

## 3. Provenance Chain Rules

1. **Entry Point**: Every external request (API call, webhook, scheduled job) must generate a new `trace_id`.
2. **Propagation**: `trace_id` must be propagated to all downstream calls, event emissions, and external integrations.
3. **Immutability**: `trace_id`, `span_id`, and `parent_span_id` are immutable once set.
4. **Linkage**: Every state transition and event must reference the `trace_id` of the operation that caused it.

## 4. Provenance Requirements by Entity

### PrintJob

- Every state transition must record the `trace_id` that caused it.
- Every event emitted by the job must carry the job's `trace_id`.
- Retry attempts must generate new `trace_id`s but reference the original via `correlation_id`.

### PrintExecution

- `trace` is captured at execution start and must not change.
- All execution events must reference the execution's `trace_id`.
- Provider interactions must propagate the execution's `trace_id`.

### Printer

- Observations must carry the provider's `trace_id`.
- Status changes triggered by observations must record both the observation's `trace_id` and the reconciliation `trace_id`.

### Document

- Document ingest must carry the `trace_id` of the originating request.
- Document retrieval must carry the `trace_id` of the requesting operation.

## 5. Audit Trail

- The system must maintain an append-only audit trail of all provenance chains.
- Audit records must include:
  - `trace_id`
  - `aggregate_id`
  - `aggregate_type`
  - `action`
  - `timestamp`
  - `actor` (system, user, provider)
- Audit records must be immutable and tamper-evident.
- Audit retention must comply with organizational policies (default: 7 years).

## 6. Cryptographic Provenance

- Critical state transitions (e.g., job completion, payment, security-sensitive operations) must include a cryptographic signature.
- Signatures must be generated using an HSM or KMS.
- Signatures must cover:
  - The state transition payload.
  - The `trace_id`.
  - The `timestamp`.
  - The actor's identity.

## 7. Provenance Queries

- The system must support querying the full provenance chain by `trace_id`.
- The system must support querying all operations affecting a specific aggregate.
- Provenance queries must be audit-logged.

## 8. Violations

- Any state change without proper provenance must be rejected.
- Any event with a missing or invalid `trace_id` must be logged as a security incident.
- The system must alert on provenance chain breaks.
