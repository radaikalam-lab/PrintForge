# ADR-008: Epistemic Status Model

## Status

Accepted

## Context

Observations, declarations, and derived signals about printer state and capabilities need a clear vocabulary. A single mixed status value (e.g., "OK", "WARNING", "ERROR") is insufficient because it conflates source, freshness, and consistency.

## Decision

We use independent dimensions for epistemic status:

### Source
- OBSERVED — directly observed by provider
- DECLARED — declared by provider without verification
- DERIVED — derived from other observations
- ASSUMED — assumed for control plane operation

### Freshness
- FRESH — within freshness threshold
- STALE — older than staleness threshold
- EXPIRED — older than expiration threshold
- UNKNOWN — freshness is unknown

### Consistency
- CONSISTENT — no conflict detected
- CONTRADICTED — contradicted by subsequent evidence
- UNKNOWN — consistency is unknown

### Confidence

Confidence is not mandated as a numeric value in this version. If confidence is represented, its semantics must be defined before use.

## Consequences

### Positive

- Status dimensions are orthogonal and composable.
- Contradictions are explicit (CONTRADICTED) rather than silently resolved.
- Stale observations remain identifiable (STALE) and cannot silently become fresh.

### Negative

- More complex status representation than a single enum.
- Consumers must understand multiple dimensions.

### Neutral

- This model is similar to knowledge representation in distributed systems.
- The epistemic subsystem enforces these dimensions at the boundary.

## Alternatives Considered

1. **Single status enum**: One value combining all dimensions. Rejected because it conflates orthogonal concerns and makes contradictions invisible.
2. **Numeric confidence score**: A single float representing trust. Rejected because it is ambiguous and can silently change.

## References

- OBSERVATION_EVIDENCE_CONTRACT.md
- EPISTEMIC_BOUNDARY_CONTRACT.md
- EPISTEMIC_PROVENANCE_CONTRACT.md
- domain/observation.py
