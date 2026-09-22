# ADR-002: Single Writer State Ownership

## Status

Accepted

## Context

Multiple components in PrintForge observe, propose, or execute actions that affect print jobs. Without a clear ownership model, state mutations can come from multiple sources, leading to race conditions, inconsistent state, and difficult-to-debug behavior.

## Decision

**Job Manager is the sole writer of PrintJob lifecycle state.**

Other components may produce decisions, observations, or execution results, but may not directly mutate PrintJob state.

Component outputs:

| Component | Produces | Does not mutate |
|-----------|----------|-----------------|
| Scheduler | SchedulingDecision | PrintJob state |
| Policy Engine | PolicyDecision | PrintJob state |
| Provider | ExecutionResult | PrintJob state |
| Observation Engine | Observation / ReconciledObservation | PrintJob state |
| Job Manager | State transition | — (sole writer) |

The Job Manager consumes validated decisions and results and performs legal state transitions through the state machine defined in domain/state_machines.py.

## Consequences

### Positive

- PrintJob state changes are deterministic and auditable.
- Race conditions are impossible because there is exactly one writer.
- Testing is simplified: state transitions are predictable.

### Negative

- Additional plumbing is required to pass decisions/results to the Job Manager.
- Components cannot "just fix" state — they must go through the Job Manager.

### Neutral

- This pattern is consistent with event-sourced and CQRS architectures.
- The Job Manager becomes a critical path component; it must be highly available.

## Alternatives Considered

1. **Multi-writer with optimistic locking**: Multiple components could write with conflict resolution. Rejected because it adds complexity and non-determinism.
2. **Provider-owned job state**: Providers could update job state directly. Rejected because providers are external and may fail or be unavailable.

## References

- PRINTFORGE_SYSTEM_CONTRACT.md
- PRINT_JOB_CONTRACT.md
- domain/state_machines.py
