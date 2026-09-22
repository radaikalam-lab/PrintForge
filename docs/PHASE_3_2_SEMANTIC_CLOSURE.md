# Phase 3.2 Semantic Closure

## Summary

Phase 3.2 closes semantic inconsistencies identified during architecture review of Phase 3 / Architecture v0.3. Phase 3 implementation remains valid; this document captures architecture clarification and implementation corrections.

## Issues found and resolved

### 1. FAILED state machine contradiction

**Issue**: The architecture referred to `PROCESSING → FAILED` but FAILED was missing from the PrintJob state table in some contexts.

**Resolution**: FAILED is confirmed as a terminal PrintJob state. `PROCESSING → FAILED` is explicitly added to the transition table with cause "Retries exhausted or failure is non-retryable."

### 2. REJECTED semantics contradiction

**Issue**: REJECTED was declared terminal but also described as retryable against another provider.

**Resolution**: REJECTED is removed from PrintJobState and added to ExecutionState. Provider rejection is an ExecutionAttempt result, not a PrintJob terminal state. The PrintJob remains in SUBMITTED. The Scheduler may create a new ExecutionAttempt with an alternative provider. If no alternative provider is available, the PrintJob transitions to FAILED.

### 3. Missing SCHEDULED → QUEUED rescheduling transition

**Issue**: Architecture described provider unreachability causing rescheduling, but the transition table lacked `SCHEDULED → QUEUED`.

**Resolution**: Added `SCHEDULED → QUEUED` with cause "Provider unreachable before submission / reschedule."

### 4. Capability reconciliation vocabulary

**Issue**: The reconciliation table contained `ACCEPTED_OBSERVED`, which conflated source and outcome dimensions.

**Resolution**: Replaced with `ACCEPTED`. Updated `CapabilityReconciliationStatus` enum in domain/capabilities.py to use closed vocabulary: ACCEPTED, ACCEPTED_WITH_STALE_EVIDENCE, CONFLICT, UNRESOLVED, UNAVAILABLE.

### 5. Invalid capability example

**Issue**: Architecture example used `duplex = failed`, conflating capability values with execution outcomes.

**Resolution**: Replaced with `duplex = unsupported`. Added explicit note in CAPABILITY_CONTRACT.md that capability values are distinct from observation/query execution results.

### 6. Observation Engine vs Epistemic Subsystem ownership

**Issue**: Observation Engine was described as owning "epistemic record creation," overlapping with Epistemic Subsystem responsibility.

**Resolution**: Clarified ownership:
- Observation Engine: ingestion, normalization, raw evidence preservation, provenance capture, forwarding evidence
- Epistemic Subsystem: epistemic qualification, freshness/consistency evaluation, reconciliation, EpistemicRecord creation
- Job Manager: PrintJob lifecycle mutation

### 7. ExecutionAttempt transition semantics

**Issue**: ExecutionAttempt states were defined but legal transitions were not.

**Resolution**: Added explicit ExecutionAttempt transition table covering SUBMITTED, PROCESSING, COMPLETED, FAILED, CANCELLED, REJECTED, and UNKNOWN states.

### 8. Duplicate authority text

**Issue**: Sections 1 and 1.1 in ARCHITECTURE.md contained duplicate authority model text.

**Resolution**: Merged into a single section with an authority definitions table.

### 9. Epistemic principle naming

**Issue**: Inconsistent naming ("Epistemic Novelty ≠ Production Authority" vs "Epistemic Status ≠ Production Authority").

**Resolution**: Standardized to "Epistemic Status ≠ Production Authority" throughout.

### 10. Architecture diagram semantics

**Issue**: Epistemic Subsystem was depicted as a Domain Core adapter rather than an advisory overlay.

**Resolution**: Redesigned diagram to show Epistemic Subsystem as an advisory overlay above the Application Layer.

### 11. NFR handling

**Issue**: Latency, throughput, and disaster recovery marked as TBD without explanation.

**Resolution**: Added explicit note that TBD items are deployment-profile-specific and not architectural contradictions.

### 12. tenant_id wording

**Issue**: `tenant_id: reserved/TBD` was ambiguous.

**Resolution**: Changed to `tenant_id: reserved` with explicit note that multi-tenancy is deferred.

## Implementation changes

| File | Change |
|------|--------|
| domain/job.py | Removed REJECTED from PrintJobState |
| domain/state_machines.py | Removed SUBMITTED→REJECTED and REJECTED→ARCHIVED; added SCHEDULED→QUEUED |
| domain/execution.py | Added REJECTED to ExecutionState |
| domain/capabilities.py | Updated CapabilityReconciliationStatus enum |
| tests/unit/test_execution_attempts.py | Added REJECTED tests, removed REJECTED from terminal states |
| tests/epistemic/test_capability_reconciliation.py | Updated to use new reconciliation status values |
| docs/ARCHITECTURE.md | Updated to v0.3 with all semantic closures |
| docs/contracts/PRINT_JOB_CONTRACT.md | Updated state machine to match implementation |
| docs/contracts/EXECUTION_CONTRACT.md | Updated ExecutionState to match implementation |
| docs/contracts/CAPABILITY_CONTRACT.md | Fixed reconciliation vocabulary and example |
| docs/contracts/OBSERVATION_CONTRACT.md | Removed AGING references |
| docs/contracts/OBSERVATION_EVIDENCE_CONTRACT.md | Removed AGING, added EXPIRED |
| docs/contracts/API_CONTRACT.md | Changed PENDING to CREATED |
| docs/adr/ADR-009-observation-reconciliation.md | Fixed example (duplex = unsupported) |
| docs/adr/ADR-010-capability-reconciliation-dimensions.md | Fixed ACCEPTED_OBSERVED → ACCEPTED |

## Tests added

1. `test_scheduled_to_queued_rescheduling` — SCHEDULED → QUEUED transition
2. `test_execution_attempt_rejected_represents_provider_rejection` — ExecutionAttempt REJECTED
3. `test_print_job_does_not_use_rejected_state` — REJECTED not in PrintJobState
4. `test_execution_attempt_states` — includes REJECTED
5. Updated `test_archived_is_terminal_from_all_terminal_states` — removed REJECTED

## Final verification

| Check | Result |
|-------|--------|
| pytest -q | 69 passed, 2 skipped |
| ruff | PASS |
| mypy | PASS (59 source files) |

## Remaining limitations

- StarletteDeprecationWarning from dependency (fastapi/starlette testclient) — not fixable in our code
- NFR values (latency, throughput, disaster recovery) remain TBD — deployment-profile-specific
- Multi-tenancy (tenant_id) remains reserved — deferred to future phase

## Architecture status

**SEMANTICALLY CLOSED**

Phase 4 readiness:

**READY**
