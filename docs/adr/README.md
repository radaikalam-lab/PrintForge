# PrintForge ADR Index

## Status

Active ADRs are listed below. Superseded ADRs are preserved for historical reference.

## Canonical ADR Sequence

| ADR | Title | Status |
|-----|-------|--------|
| ADR-001 | Authority Model | Accepted |
| ADR-002 | Single-Writer State Ownership | Accepted |
| ADR-003 | Provider Architecture | Accepted |
| ADR-004 | Provider Isolation | Accepted |
| ADR-005 | IPP as Protocol Boundary | Accepted |
| ADR-006 | CUPS and PAPPL Integration | Accepted |
| ADR-007 | Deterministic Core | Accepted |
| ADR-008 | Epistemic Status Model | Accepted |
| ADR-009 | Observation Reconciliation | Accepted |
| ADR-010 | Capability Reconciliation Dimensions | Accepted |
| ADR-011 | Provenance Model | Accepted |
| ADR-012 | Event Delivery Semantics | Accepted |
| ADR-013 | Execution Attempt Model | Accepted |
| ADR-014 | UNKNOWN Semantics | Accepted |
| ADR-015 | Policy Engine Boundary | Accepted |
| ADR-016 | Spool Architecture | Accepted |
| ADR-017 | Persistence Abstraction | Accepted |
| ADR-018 | Document Representation | Accepted |
| ADR-019 | Docker and Linux Deployment | Accepted |
| ADR-020 | Simulation-First Development | Accepted |
| ADR-021 | Physical Hardware Boundary | Accepted |
| ADR-022 | Observation Engine and Epistemic Subsystem Boundary | Accepted |

## Major Architectural Relationships

### Authority and State Ownership

- ADR-001 establishes the observation-based authority model.
- ADR-002 establishes Job Manager as the sole writer of PrintJob lifecycle state.
- ADR-004 establishes provider isolation boundaries.

### Execution Model

- ADR-013 establishes ExecutionAttempt as a first-class entity separate from PrintJob lifecycle.
- ADR-014 defines UNKNOWN as an ExecutionAttempt/epistemic state, not a PrintJob state.
- ADR-015 defines the Policy Engine boundary.

### Epistemic Model

- ADR-008 defines independent epistemic dimensions (Source, Freshness, Consistency).
- ADR-009 defines observation reconciliation and defers to ADR-010 for the canonical multidimensional model.
- ADR-010 defines the canonical capability reconciliation vocabulary.
- ADR-011 defines the provenance model.
- ADR-022 defines the Observation Engine / Epistemic Subsystem ownership boundary.

### Provider and Protocol

- ADR-003 defines the provider plugin architecture.
- ADR-005 defines IPP as the canonical protocol boundary.
- ADR-006 defines CUPS and PAPPL integration.
- ADR-021 defines the physical hardware boundary.

### Infrastructure

- ADR-007 defines the deterministic core.
- ADR-012 defines event delivery semantics.
- ADR-016 defines spool architecture.
- ADR-017 defines persistence abstraction.
- ADR-018 defines document representation.
- ADR-019 defines Docker and Linux deployment.
- ADR-020 defines simulation-first development.

## Chronological Ordering

ADRs are listed in canonical order above.

## Superseded ADRs

No ADRs have been superseded in this collection. All 22 ADRs are active. Consistency is maintained through reconciliation and review at phase boundaries.

## Open / Deferred Decisions

The following decisions are intentionally deferred and are not architectural inconsistencies:

- **CUPS/PAPPL final deployment mechanism**: The core maintains the non-root container principle. CUPS/PAPPL adapters may require elevated privileges or device access; the final deployment mechanism is deferred to a future operational ADR.
- **Multi-tenancy / `tenant_id`**: Reserved for future use. Not implemented in the current scope.
- **NFR numerical targets**: Latency, throughput, and disaster recovery values are deployment-profile-specific and will be resolved through future operational/deployment ADRs before production deployment.

## Adding New ADRs

When adding a new ADR:
1. Assign the next available number (currently ADR-023).
2. Do not reuse existing numbers.
3. Cross-reference related ADRs.
4. Use status consistently: Proposed, Accepted, Amended, Superseded, Deprecated.
