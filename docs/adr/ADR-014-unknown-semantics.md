# ADR-014: UNKNOWN Semantics

## Status

Accepted

## Context

UNKNOWN was previously used as a PrintJob lifecycle state, conflating application lifecycle uncertainty with execution state uncertainty. This made it impossible to distinguish between "the job's lifecycle state is uncertain" and "the execution state is uncertain because the provider lost connection."

## Decision

UNKNOWN is removed from the PrintJob lifecycle. PrintJob lifecycle represents the known application lifecycle.

UNKNOWN belongs to ExecutionAttempt state and epistemic execution status.

Example:

```text
PrintJob:
    lifecycle = PROCESSING

ExecutionAttempt:
    state = UNKNOWN

Epistemic:
    consistency = UNKNOWN
    freshness = STALE

Reason:
    provider connection lost
```

UNKNOWN entry and exit conditions are explicit:
- Entry: provider connection lost, timeout without response, or observation gap exceeds threshold
- Exit: provider responds, explicit cancellation, or explicit failure/completion observed

UNKNOWN is not a convenient catch-all state. It represents genuine uncertainty about execution state.

## Consequences

### Positive

- PrintJob lifecycle is clean and deterministic.
- Execution uncertainty is isolated to ExecutionAttempt.
- Operators can distinguish between "job is being processed" and "we don't know if the printer is processing."

### Negative

- More states to track and display.
- Consumers must handle UNKNOWN explicitly.

### Neutral

- This is consistent with distributed systems patterns where observation uncertainty is separated from logical state.
- The epistemic subsystem qualifies UNKNOWN with freshness and consistency.

## Alternatives Considered

1. **Keep UNKNOWN in PrintJob lifecycle**: Simple but conflates concerns. Rejected.
2. **Remove UNKNOWN entirely**: Would require representing uncertainty differently. Rejected because uncertainty is a real operational state.

## References

- ARCHITECTURE.md
- EXECUTION_CONTRACT.md
- EPISTEMIC_BOUNDARY_CONTRACT.md
