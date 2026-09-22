# ADR-011: Provenance Model

## Status

Accepted

## Context

Every state change, event, and observation in PrintForge must carry an immutable provenance chain. Without a standardized provenance model, audit trails are incomplete and causal relationships are lost.

## Decision

Every external observation and domain event retains a provenance chain with at minimum:

| Field | Description |
|-------|-------------|
| source_id | Unique identifier for the observation source |
| provider | Provider identifier |
| provider_version | Provider version |
| actor | Entity that produced the observation |
| timestamp | Observation timestamp |
| correlation_id | Correlation identifier |
| causal_reference | Domain-level causal chain reference |

TraceContext provides:

| Field | Description |
|-------|-------------|
| trace_id | UUID v7 identifying the causal chain |
| span_id | UUID v7 identifying the current operation |
| parent_span_id | Parent operation or null |
| baggage | Key-value pairs propagated across boundaries |

Provenance is never discarded because data has been normalized. Normalized data and provenance remain separable.

### Causality relationship

Event envelopes use `causation_id` to identify the immediate event cause (see ADR-012). Provenance records use `causal_reference` to capture the domain-level causal chain. When an event causes a provenance-bearing state change, its `causation_id` may populate the corresponding provenance `causal_reference`.

## Consequences

### Positive

- Every fact can be traced back to its source.
- Audit logs are complete and tamper-evident.
- Debugging production issues is feasible.

### Negative

- Provenance data adds storage overhead.
- Every producer must populate provenance fields correctly.

### Neutral

- This model is consistent with OpenTelemetry trace context.
- Provenance queries must be audit-logged.

## Alternatives Considered

1. **No provenance**: State changes without traceability. Rejected because it makes debugging and compliance impossible.
2. **Best-effort provenance**: Provenance is optional. Rejected because gaps in provenance chains are unacceptable.

## References

- PROVENANCE_CONTRACT.md
- EPISTEMIC_PROVENANCE_CONTRACT.md
- EVENT_CONTRACT.md
