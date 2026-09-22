# ADR-005: Observation Reconciliation

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

Reconciliation status values:

| Status | Meaning |
|--------|---------|
| DECLARED | Only declared capabilities available; no observation received |
| OBSERVED | Observed capabilities match declared capabilities |
| CONTRADICTED | Observed capabilities differ from declared capabilities |
| UNAVAILABLE | Observation unavailable; declared capabilities remain the only source of truth |

Stale observations participate in reconciliation and are marked CONTRADICTED when they conflict with declarations, but remain identifiable as stale.

## Consequences

### Positive

- Contradictions are visible and auditable.
- Operators can investigate discrepancies rather than being misled by silent overwrites.
- The system never fabricates capabilities.

### Negative

- Contradicted printers require operator intervention.
- Routing must handle CONTRADICTED status explicitly.

### Neutral

- This is similar to CRDT conflict resolution where both sides are preserved.
- The domain contract for PrinterCapabilities does not permit mutation based on observation.

## Alternatives Considered

1. **Observation wins**: Observed capabilities overwrite declarations. Rejected because it violates the authority model and loses declared intent.
2. **Declaration wins**: Observed capabilities are discarded when they conflict. Rejected because it hides real-world printer behavior.

## References

- CAPABILITY_CONTRACT.md
- OBSERVATION_EVIDENCE_CONTRACT.md
- domain/capabilities.py
