# ADR-013: Execution Attempt Model

## Status

Accepted

## Context

Retries in the original PrintJob state machine were represented as lifecycle transitions (FAILED → QUEUED). This conflated the logical print request (PrintJob) with individual provider execution attempts and made retry history implicit and lossy.

## Decision

Retries are represented by separate ExecutionAttempt entities, not PrintJob lifecycle transitions.

```text
PrintJob
   │
   ├── ExecutionAttempt 1
   │       └── result
   │
   ├── ExecutionAttempt 2
   │       └── result
   │
   └── ExecutionAttempt N
           └── result
```

The parent PrintJob represents the logical print request. ExecutionAttempt represents an individual provider/device execution attempt.

Every attempt records:
- attempt_id (conceptual identifier; implemented as `PrintExecution.execution_id` in the current domain model)
- job_id
- provider
- printer_id
- start_time
- end_time
- requested_operation
- result
- failure_information
- provenance
- correlation_id

Terminology mapping:
- Conceptual `attempt_id` maps to `PrintExecution.execution_id` in the current implementation.
- The domain entity `PrintExecution` is the concrete representation of `ExecutionAttempt`.
- Provider interfaces return `PrintExecution` objects from `submit()` and `control()` methods.

A retry creates a new ExecutionAttempt. The parent PrintJob remains non-terminal while retryable execution attempts exist. Previous attempt history is preserved.

## Consequences

### Positive

- Retry history is explicit and auditable.
- PrintJob lifecycle remains clean; execution attempts carry their own state.
- Terminal states are unambiguous: FAILED is terminal for the PrintJob only when no retryable attempts remain.

### Negative

- More entities to track and query.
- Consumers must understand the PrintJob/ExecutionAttempt relationship.

### Neutral

- This is a standard pattern in job orchestration systems.
- The PrintExecution domain model maps directly to ExecutionAttempt.

## Alternatives Considered

1. **PrintJob lifecycle transitions for retries**: FAILED → QUEUED for retry. Rejected because it makes FAILED non-terminal and loses attempt history.
2. **Retry counter on PrintJob**: Simple but loses per-attempt detail. Rejected because it doesn't preserve provenance per attempt.

## References

- ARCHITECTURE.md
- PRINT_JOB_CONTRACT.md
- EXECUTION_CONTRACT.md
- domain/execution.py
