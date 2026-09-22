# Phase 3.1 Architecture Reconciliation

## Summary

Architecture v0.3 reconciliation resolves semantic inconsistencies identified during architecture review. Phase 3 implementation remains valid; this document captures architecture clarification and minor implementation corrections.

## Changes from v0.2

### State machine corrections

- Removed `FAILED → QUEUED` transition. FAILED is terminal for the PrintJob. Retries are modeled as new ExecutionAttempt entities, not lifecycle rollbacks.
- Added `BLOCKED` state for jobs with no capable printer or provider.
- Added `ARCHIVED` as explicit terminal state reachable from any terminal state via retention policy.
- Removed `UNKNOWN` from PrintJobState. UNKNOWN belongs to ExecutionAttempt state and epistemic status.

### ExecutionAttempt model

Introduced the ExecutionAttempt model as a first-class concept:

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

Every attempt has:
- attempt_id
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

### Failure paths

Explicitly modeled:
- No capable printer → QUEUED → BLOCKED
- Provider unreachable before submission → remains QUEUED/SCHEDULED
- Provider timeout after submission → ExecutionAttempt UNKNOWN, PrintJob remains PROCESSING
- Provider rejection before submission → PrintJob REJECTED
- Provider failure after accepted submission → ExecutionAttempt FAILED or UNKNOWN

### Epistemic dimensions

Separated into independent dimensions:
- Source: OBSERVED, DECLARED, DERIVED, ASSUMED
- Freshness: FRESH, STALE, EXPIRED, UNKNOWN
- Consistency: CONSISTENT, CONTRADICTED, UNKNOWN
- Reconciliation outcome: ACCEPTED, ACCEPTED_WITH_STALE_EVIDENCE, CONFLICT, UNRESOLVED, UNAVAILABLE

Removed AGING from freshness dimensions (not semantically necessary).

### Capability reconciliation

Updated to use independent dimensions rather than a single status enum.

### Epistemic principle

Renamed from "Epistemic Novelty ≠ Production Authority" to "Epistemic Status ≠ Production Authority."

## Implementation changes

| File | Change |
|------|--------|
| domain/job.py | Removed UNKNOWN, added BLOCKED and ARCHIVED |
| domain/state_machines.py | Updated transitions, removed FAILED→QUEUED, added BLOCKED/ARCHIVED |
| domain/execution.py | Renamed PENDING→SUBMITTED, removed ACCEPTED/REJECTED, added CANCELLED |
| simulation/simulator.py | Updated ExecutionState.ACCEPTED → SUBMITTED |
| tests/integration/test_pipeline.py | Updated ExecutionState.ACCEPTED → SUBMITTED |
| tests/helpers/fake_providers.py | Updated ExecutionState.ACCEPTED → SUBMITTED |
| tests/unit/test_execution_attempts.py | New tests for execution attempts, retry, BLOCKED, ARCHIVED, UNKNOWN |

## Documentation changes

| File | Change |
|------|--------|
| docs/ARCHITECTURE.md | Updated to v0.3 |
| docs/adr/ADR-013-execution-attempt-model.md | New |
| docs/adr/ADR-014-unknown-semantics.md | New |
| docs/adr/ADR-010-capability-reconciliation-dimensions.md | New |

## Phase 3 baseline

Phase 3 freeze remains valid. The historical Phase 3 verification is reproducible.

## Next phase

Phase 4 — Spool and Document Pipeline
