# ADR-010: Capability Reconciliation Dimensions

## Status

Accepted

## Context

The original capability reconciliation model used a single status value (DECLARED, OBSERVED, CONTRADICTED, UNAVAILABLE) that conflated source, freshness, and consistency. This made it impossible to represent "observed but stale" or "contradicted but fresh" without adding more enum values.

## Decision

Capability reconciliation uses independent dimensions:

| Declared    | Observed    | Freshness | Consistency  | Reconciliation               |
| ----------- | ----------- | --------- | ------------ | ---------------------------- |
| supported   | supported   | FRESH     | CONSISTENT   | ACCEPTED                     |
| supported   | unsupported | FRESH     | CONTRADICTED | CONFLICT                     |
| supported   | supported   | STALE     | CONSISTENT   | ACCEPTED_WITH_STALE_EVIDENCE |
| unknown     | supported   | FRESH     | UNKNOWN      | ACCEPTED            |
| supported   | unavailable | UNKNOWN   | UNKNOWN      | UNRESOLVED                   |
| unsupported | supported   | FRESH     | CONTRADICTED | CONFLICT                     |

Source values (OBSERVED, DECLARED, DERIVED, ASSUMED) are not used as reconciliation outcomes.
Freshness values (FRESH, STALE, EXPIRED, UNKNOWN) are not used as capability values.
Consistency values (CONSISTENT, CONTRADICTED, UNKNOWN) are not used as reconciliation outcomes.

The reconciliation outcome is a separate dimension.

## Consequences

### Positive

- Reconciliation is unambiguous and composable.
- Operators can see exactly what conflicted and why.
- The system never silently overwrites declarations or observations.

### Negative

- More complex reconciliation logic.
- Consumers must understand four dimensions instead of one.

### Neutral

- This is similar to multi-dimensional status models in monitoring systems.
- The CapabilityReconciliation model in domain/capabilities.py carries all dimensions.

## Alternatives Considered

1. **Single reconciliation enum**: Simpler but conflates dimensions. Rejected.
2. **Source wins / Observation wins**: Implicit resolution. Rejected because it hides contradictions.

## References

- ARCHITECTURE.md v0.3
- CAPABILITY_CONTRACT.md
- domain/capabilities.py
