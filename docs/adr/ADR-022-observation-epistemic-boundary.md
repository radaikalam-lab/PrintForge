# ADR-022: Observation Engine and Epistemic Subsystem Boundary

## Status

Accepted

## Context

PrintForge receives observations from providers about printer state and capabilities. These observations must be ingested, normalized, and qualified before they can inform application decisions. During Phase 3, the responsibilities for ingestion and epistemic qualification were not clearly separated, creating risk of duplicate conceptual ownership.

## Decision

The Observation Engine and Epistemic Subsystem have distinct, non-overlapping responsibilities.

### Observation Engine owns

- ingestion of provider observations
- normalization
- observation envelope creation
- preservation of raw evidence
- provenance capture
- forwarding evidence for epistemic evaluation

### Epistemic Subsystem owns

- epistemic qualification
- freshness evaluation
- consistency evaluation
- reconciliation
- EpistemicRecord creation

### Job Manager owns

- interpretation of authorized application-level inputs
- PrintJob lifecycle mutation

The Observation Engine must not create EpistemicRecords. The Epistemic Subsystem must not directly execute providers or mutate production state.

The following path is prohibited:

```text
Epistemic
   ↓
Provider
   ↓
Printer
```

## Consequences

### Positive

- Clear ownership prevents duplicate conceptual work.
- The epistemic layer remains advisory and cannot accidentally become an execution path.
- Observability is improved because raw evidence and epistemic qualification are separable.

### Negative

- Additional plumbing is required to forward evidence from the Observation Engine to the Epistemic Subsystem.
- Consumers must understand the distinction between raw observation and epistemic qualification.

### Neutral

- This separation is similar to sensor ingestion vs. sensor fusion in control systems.
- The Observation Engine may be reused for non-epistemic purposes (e.g., raw telemetry logging).

## Alternatives Considered

1. **Unified Engine**: A single component ingests, normalizes, and qualifies observations. Rejected because it conflates raw evidence with interpretation and makes the epistemic boundary permeable.
2. **Epistemic Engine owns everything**: The epistemic layer ingests and qualifies. Rejected because it gives the advisory layer too much control over raw data flow.

## References

- ARCHITECTURE.md v0.3
- EPISTEMIC_BOUNDARY_CONTRACT.md
- OBSERVATION_EVIDENCE_CONTRACT.md
- EPISTEMIC_PROVENANCE_CONTRACT.md
