# ADR-001: Authority Model

## Status

Accepted

## Context

PrintForge must maintain clear authority boundaries between its own application state, provider execution, physical printer reality, and epistemic advisory functions. The previous formulation "system observes but does not directly control printers" was ambiguous and did not distinguish between the multiple authority scopes involved.

## Decision

We define four distinct authority scopes:

1. **PrintForge application authority**: The Job Manager owns PrintJob lifecycle state. All other components may propose but not mutate.
2. **Provider execution authority**: Providers translate application intents into printer-specific operations. Providers do not own domain state.
3. **Printer physical authority**: Physical printers are authoritative for physical reality. Provider observations report but do not control physical state.
4. **Epistemic advisory authority**: The epistemic subsystem qualifies observations. It informs decisions but cannot authorize execution or mutate production state.

The governing principle is:

> **Observation-based authority:** PrintForge derives authoritative application state from validated observations and explicit application transitions. Providers may execute printer operations under contract, but providers cannot directly mutate domain state.

## Consequences

### Positive

- Authority boundaries are explicit and enforceable.
- Each component has a clear, non-overlapping responsibility.
- Epistemic information cannot be mistaken for production authority.

### Negative

- More ceremony in cross-component communication.
- Requires explicit handoff points between authority scopes.

### Neutral

- This model is similar to other control-plane systems (e.g., Kubernetes).
- The epistemic layer is strictly advisory; it never directly causes side effects.

## Alternatives Considered

1. **Unified authority**: All components could read and write domain state freely. Rejected because it eliminates accountability and makes bugs harder to trace.
2. **Provider authority**: Providers could own domain state for printers they manage. Rejected because it breaks the single-writer rule and creates race conditions.

## References

- PRINTFORGE_SYSTEM_CONTRACT.md
- OBSERVATION_CONTRACT.md
- EPISTEMIC_BOUNDARY_CONTRACT.md
