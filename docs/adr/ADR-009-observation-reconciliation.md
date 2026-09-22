# ADR-009: Observation Reconciliation

## Status

Accepted

## Context

Declared capabilities and observed capabilities may conflict. The system must handle these conflicts explicitly rather than silently choosing one source.

## Decision

When declared and observed capabilities conflict, the system represents the contradiction explicitly:

```text
DECLARED:
    duplex = supported

OBSERVED:
    duplex = unsupported

CONSISTENCY:
    CONTRADICTED
```

Both declaration and observation are preserved with full provenance. Neither is silently overwritten.

The canonical reconciliation model uses independent dimensions defined in ADR-010:

- **Source**: OBSERVED, DECLARED, DERIVED, ASSUMED
- **Freshness**: FRESH, STALE, EXPIRED, UNKNOWN
- **Consistency**: CONSISTENT, CONTRADICTED, UNKNOWN
- **Reconciliation outcome**: ACCEPTED, ACCEPTED_WITH_STALE_EVIDENCE, CONFLICT, UNRESOLVED, UNAVAILABLE

ADR-009 defers to ADR-010 for the canonical multidimensional reconciliation vocabulary and rules.

## Consequences

### Positive

- Contradictions are visible and auditable.
- Operators can investigate discrepancies rather than being misled by silent overwrites.
- The system never fabricates capabilities.
- Reconciliation dimensions are independent and composable.

### Negative

- Contradicted printers require operator intervention.
- Routing must handle CONFLICT status explicitly.

### Neutral

- This is similar to CRDT conflict resolution where both sides are preserved.
- The domain contract for PrinterCapabilities does not permit mutation based on observation.

## Alternatives Considered

1. **Observation wins**: Observed capabilities overwrite declarations. Rejected because it violates the authority model and loses declared intent.
2. **Declaration wins**: Observed capabilities are discarded when they conflict. Rejected because it hides real-world printer behavior.

## References

- ADR-010: Capability Reconciliation Dimensions
- CAPABILITY_CONTRACT.md
- OBSERVATION_EVIDENCE_CONTRACT.md
- domain/capabilities.py
