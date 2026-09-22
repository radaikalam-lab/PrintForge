# PrintForge Architecture

Document: PrintForge Architecture
Version: 0.3
Status: Implementation Baseline — Architecture Reconciled
Owner: PrintForge Architecture
Last Updated: 2026-09-22
Review: At major phase boundaries
Supersedes: Architecture v0.2

## 1. Architecture Authority Model

PrintForge derives authoritative application state from validated observations and explicit application transitions. Providers may execute printer operations under contract, but providers cannot directly mutate domain state.

Four distinct authority scopes are defined:

```text
PrintForge application authority
Provider execution authority
Printer physical authority
Epistemic advisory authority
```

### 1.1 Authority definitions

| Authority scope | Description |
|-----------------|-------------|
| PrintForge application authority | The Job Manager owns PrintJob lifecycle state. All other components may propose but not mutate. |
| Provider execution authority | Providers translate application intents into printer-specific operations. Providers do not own domain state. |
| Printer physical authority | Physical printers are authoritative for physical reality. Provider observations report but do not control physical state. |
| Epistemic advisory authority | The epistemic subsystem qualifies observations. It informs decisions but cannot authorize execution or mutate production state. |

## 2. Single-writer state ownership

**Job Manager is the sole writer of PrintJob lifecycle state.**

Other components may produce decisions, observations, or execution results, but may not directly mutate PrintJob state.

### Component outputs

| Component | Produces | Does not mutate |
|-----------|----------|-----------------|
| Scheduler | SchedulingDecision | PrintJob state |
| Policy Engine | PolicyDecision | PrintJob state |
| Provider | ExecutionResult | PrintJob state |
| Observation Engine | Observation / ReconciledObservation | PrintJob state |
| Job Manager | State transition | — (sole writer) |

## 3. State transition authority

This table is normative.

| Component           | Observe |           Propose |              Execute | Mutate Job State |
|---------------------|--------:|-----------------:|--------------------:|-----------------:|
| API                 |      Yes |               Yes |                 No  |               No |
| Job Manager         |      Yes |               Yes | Request via provider contract |              YES |
| Scheduler           |      Yes |               YES |                 No  |               No |
| Policy Engine       |      Yes |               YES |                 No  |               No |
| Observation Engine  |      YES |               YES |                 No  |               No |
| Provider Registry   |      Yes |                No |                 No  |               No |
| Provider            |      Yes |            Result |                  YES |               No |
| Epistemic subsystem |      YES |               YES |                  NO |               NO |
| Printer             | Physical | Physical response |                  YES |         External |

## 4. Provider authority

Providers may command printer operations under contract, but physical state remains authoritative at the printer.

Providers may:
- discover printers
- query capabilities
- query status
- submit jobs
- cancel jobs where supported
- retrieve execution results

Providers may NOT:
- mutate PrintJob state
- bypass policy
- bypass validation
- create authoritative domain facts without provenance
- directly invoke the epistemic subsystem to change production state

Provider output must enter the application through explicit contracts.

## 5. Unified architecture diagram

PrintForge uses a ports-and-adapters architecture. The epistemic subsystem is an advisory overlay, not an execution adapter.

```text
                         ┌───────────────────────┐
                         │ Epistemic Subsystem   │
                         │ Advisory / Qualifying │
                         └───────────┬───────────┘
                                     │
                                     ▼
API / Intent
     ↓
Application Layer
     ├── Job Manager
     ├── Scheduler
     ├── Policy Engine
     └── Observation Engine
     ↓
Domain Core
     ↓
Ports
 ┌──────────────┬──────────────┬──────────────┐
 ▼              ▼              ▼
Provider       Spool       Persistence
Registry       Adapter       Adapter
 ▼
Provider
 ▼
Physical Printer
```

Cross-cutting concerns are shown separately and are not ordinary dependency layers:

```text
Cross-cutting:
Event Bus
Observability
Security
Audit
Configuration
```

## 6. Epistemic architecture overlay

The epistemic subsystem is an advisory/qualifying overlay.

```text
External observation
        ↓
Observation Engine
        ↓
Epistemic Record
        ↓
Epistemic interpretation
        ↓
Application decision
        ↓
Job Manager
        ↓
state transition
```

The following path is prohibited:

```text
Epistemic
   ↓
Provider
   ↓
Printer
```

Epistemic information cannot directly cause physical execution.

### 6.1 Epistemic Status ≠ Production Authority

Epistemic information may qualify, challenge, or inform production decisions, but cannot directly authorize physical execution or mutate authoritative production state.

Observations, declarations, and derived signals carry epistemic status (e.g., OBSERVED, DECLARED, ASSUMED, STALE, CONTRADICTED). They inform control-plane decisions but never execute printer operations or bypass validation. Only explicit application services and authorized provider interfaces may mutate domain state.

### 6.2 Observation Engine and Epistemic Subsystem ownership

The Observation Engine and Epistemic Subsystem have distinct, non-overlapping responsibilities.

**Observation Engine owns:**
- ingestion of provider observations
- normalization
- observation envelope creation
- preservation of raw evidence
- provenance capture
- forwarding evidence for epistemic evaluation

**Epistemic Subsystem owns:**
- epistemic qualification
- freshness evaluation
- consistency evaluation
- reconciliation
- EpistemicRecord creation

**Job Manager owns:**
- interpretation of authorized application-level inputs
- PrintJob lifecycle mutation

The Observation Engine must not itself claim ownership of EpistemicRecord creation if the Epistemic Subsystem owns it.

## 7. Epistemic terminology

Independent dimensions are used for epistemic status.

## Source

| Value | Description |
|-------|-------------|
| OBSERVED | Directly observed by provider |
| DECLARED | Declared by provider without verification |
| DERIVED | Derived from other observations |
| ASSUMED | Assumed for control plane operation |

## Freshness

| Value | Description |
|-------|-------------|
| FRESH | Within freshness threshold |
| STALE | Older than staleness threshold |
| EXPIRED | Older than expiration threshold |
| UNKNOWN | Freshness is unknown |

## Consistency

| Value | Description |
|-------|-------------|
| CONSISTENT | No conflict detected |
| CONTRADICTED | Contradicted by subsequent evidence |
| UNKNOWN | Consistency is unknown |

## Reconciliation outcome

| Value | Description |
|-------|-------------|
| ACCEPTED | Evidence is consistent and sufficient |
| ACCEPTED_WITH_STALE_EVIDENCE | Consistent but stale evidence accepted with caution |
| CONFLICT | Declared and observed capabilities contradict |
| UNRESOLVED | Evidence is insufficient or unavailable |
| UNAVAILABLE | No observation available |

## Confidence

Confidence is not mandated as a numeric value in this version. If confidence is represented, its semantics must be defined before use.

## Provenance

At minimum:

| Field | Description |
|-------|-------------|
| source_id | Unique identifier for the observation source |
| provider | Provider identifier |
| provider_version | Provider version |
| actor | Entity that produced the observation |
| timestamp | Observation timestamp |
| correlation_id | Correlation identifier |
| causal_reference | Causal reference |

## 8. Epistemic authority rules

1. Epistemic records cannot mutate production state.
2. Epistemic records cannot authorize execution.
3. Assumptions cannot satisfy hard validation unless an explicit policy permits them.
4. Stale observations cannot silently become fresh.
5. Contradictions must remain visible.
6. Unknown must not silently become false.
7. Promotion from assumption/inference to production-valid fact requires explicit domain/application authority.
8. Epistemic evidence may cause a revalidation request or verification proposal, but not direct execution.

## 9. Observation reconciliation

The reconciliation model preserves all evidence explicitly. Dimensions remain independent.

| Declared    | Observed    | Freshness | Consistency  | Reconciliation               |
| ----------- | ----------- | --------- | ------------ | ---------------------------- |
| supported   | supported   | FRESH     | CONSISTENT   | ACCEPTED                     |
| supported   | unsupported | FRESH     | CONTRADICTED | CONFLICT                     |
| supported   | supported   | STALE     | CONSISTENT   | ACCEPTED_WITH_STALE_EVIDENCE |
| unknown     | supported   | FRESH     | UNKNOWN      | ACCEPTED                     |
| supported   | unavailable | UNKNOWN   | UNKNOWN      | UNRESOLVED                   |
| unsupported | supported   | FRESH     | CONTRADICTED | CONFLICT                     |

Contradictions are represented explicitly. Declarations and observations are never silently overwritten. Both are preserved with provenance.

Example:

```text
DECLARED:
    duplex = supported

OBSERVED:
    duplex = unsupported

CONSISTENCY:
    CONTRADICTED
```

## 10. PrintJob lifecycle and ExecutionAttempt

The PrintJob lifecycle represents the logical print request. ExecutionAttempt represents an individual provider/device execution attempt.

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

### 10.1 PrintJob lifecycle

| State | Terminal | Description |
|-------|----------|-------------|
| CREATED | No | Job accepted, not yet validated |
| VALIDATED | No | Validation passed |
| QUEUED | No | Queued for scheduling or waiting for capability |
| SCHEDULED | No | Scheduled to a printer |
| SUBMITTED | No | Submitted to provider |
| PROCESSING | No | Executing (one or more attempts may exist) |
| COMPLETED | Yes | All attempts completed successfully |
| VALIDATION_FAILED | Yes | Validation failed |
| CANCELLED | Yes | Cancelled by user or system |
| FAILED | Yes | Execution failed; retries exhausted or non-retryable |
| BLOCKED | No | No eligible printer or capability; may be retried later |
| ARCHIVED | Yes | Retention policy triggered; immutable |

### 10.2 PrintJob legal transitions

| From | To | Cause |
|------|----|-------|
| CREATED | VALIDATED | Validation succeeds |
| CREATED | VALIDATION_FAILED | Validation fails |
| CREATED | CANCELLED | User cancels before validation |
| VALIDATED | QUEUED | Capability match succeeds or waiting for capability |
| VALIDATED | CANCELLED | User cancels after validation |
| QUEUED | SCHEDULED | Scheduler assigns printer |
| QUEUED | BLOCKED | No eligible printer or capability |
| QUEUED | CANCELLED | User cancels while queued |
| BLOCKED | QUEUED | Capability becomes available or rescheduled |
| BLOCKED | CANCELLED | User cancels while blocked |
| SCHEDULED | SUBMITTED | Provider accepts job |
| SCHEDULED | QUEUED | Provider unreachable before submission / reschedule |
| SCHEDULED | CANCELLED | User cancels before submission |
| SUBMITTED | PROCESSING | Provider begins execution |
| SUBMITTED | CANCELLED | User cancels after submission |
| PROCESSING | COMPLETED | All attempts succeed |
| PROCESSING | FAILED | Retries exhausted or failure is non-retryable |
| PROCESSING | CANCELLED | User cancels during execution |
| PROCESSING | BLOCKED | Provider unreachable; retry authorized |
| Any terminal | ARCHIVED | Retention policy triggers |

### 10.3 ExecutionAttempt lifecycle

| State | Description |
|-------|-------------|
| SUBMITTED | Provider accepted the attempt |
| PROCESSING | Provider is executing the attempt |
| COMPLETED | Attempt completed successfully |
| FAILED | Attempt failed |
| CANCELLED | Attempt was cancelled |
| REJECTED | Provider explicitly rejected the attempt before execution |
| UNKNOWN | Execution state is uncertain (e.g., provider lost connection) |

### 10.4 ExecutionAttempt legal transitions

| From | To | Cause |
|------|----|-------|
| SUBMITTED | PROCESSING | Provider begins execution |
| SUBMITTED | COMPLETED | Provider reports immediate success |
| SUBMITTED | FAILED | Provider reports immediate failure |
| SUBMITTED | CANCELLED | Attempt cancelled before processing |
| SUBMITTED | REJECTED | Provider explicitly rejects the job |
| SUBMITTED | UNKNOWN | Provider connection lost before processing |
| PROCESSING | COMPLETED | Provider reports success |
| PROCESSING | FAILED | Provider reports failure |
| PROCESSING | CANCELLED | User cancels during execution |
| PROCESSING | UNKNOWN | Provider connection lost during execution |
| UNKNOWN | COMPLETED | Provider responds with success |
| UNKNOWN | FAILED | Provider responds with failure |
| UNKNOWN | CANCELLED | Provider confirms cancellation |
| UNKNOWN | UNKNOWN | Uncertainty persists |

### 10.5 ExecutionAttempt fields

Every attempt records:

```text
attempt_id
job_id
provider
printer_id
start_time
end_time
requested_operation
result
failure_information
provenance
correlation_id
```

### 10.6 Retry semantics

A retry creates a new ExecutionAttempt. The parent PrintJob remains non-terminal while retryable execution attempts exist.

Retry policy:
- retry policy is defined per job or globally
- maximum attempts is configurable
- retryable failures are explicitly classified
- non-retryable failures immediately terminalize the PrintJob
- retry authorization is explicit (automatic or manual)
- retry does not erase the history of previous attempts

### 10.7 Failure paths

#### No capable printer

```text
VALIDATED
    ↓
no eligible printer
    ↓
QUEUED → BLOCKED
```

The job enters BLOCKED state. It may transition back to QUEUED when a capable printer becomes available or when rescheduled.

#### Provider unreachable before submission

This is distinct from printer rejection. The job remains in SCHEDULED or QUEUED state. A timeout or health check failure transitions the provider to DEGRADED or OFFLINE. The job may be rescheduled to an alternative provider via SCHEDULED → QUEUED.

#### Provider timeout after submission

Represented as ExecutionAttempt state = UNKNOWN. The PrintJob remains in PROCESSING. A subsequent observation or provider response may resolve the UNKNOWN state. Do not automatically declare physical failure when the provider merely stopped responding.

#### Provider rejection before submission

Represented as ExecutionAttempt state = REJECTED. The provider explicitly rejected the attempt. The PrintJob remains in SUBMITTED. The Scheduler may create a new ExecutionAttempt with an alternative provider. If no alternative provider is available, the PrintJob transitions to FAILED.

#### Provider failure after accepted submission

Represented as ExecutionAttempt state = FAILED or UNKNOWN. The PrintJob may remain in PROCESSING if retry is authorized. If retry is not authorized or maximum attempts are exhausted, the PrintJob transitions to FAILED.

### 10.8 Transition record

Every PrintJob transition produces a record containing:

```text
transition_id
job_id
prior_state
new_state
actor
cause
timestamp
correlation_id
prior_state_hash
resulting_state_hash
```

## 11. Scheduler semantics

The Scheduler produces a SchedulingDecision object. It does not mutate Job state.

Example:

```yaml
scheduling_decision:
  job_id: JOB-001
  candidate_printer: PRINTER-001
  reasons:
    - capability_match
    - policy_allowed
  rejected_candidates:
    - printer_id: PRINTER-002
      reason: duplex_unsupported
```

The Job Manager validates and applies the decision.

## 12. Policy Engine

The Policy Engine produces PolicyDecision objects. It does not execute physical operations.

Responsibilities:
- authorization
- constraints
- capability requirements
- operational limits
- routing restrictions
- data handling restrictions

## 13. Provider Registry

The Provider Registry is responsible for:

- provider discovery
- provider registration
- provider capability declaration
- provider version tracking
- provider health monitoring
- provider selection metadata

Provider Registry does not own PrintJob state. It produces provider metadata that the Scheduler and Policy Engine consume.

## 14. Observation Engine

The Observation Engine is responsible for:

- ingestion of provider observations
- normalization
- observation envelope creation
- preservation of raw evidence
- provenance capture
- forwarding evidence for epistemic evaluation

It must NOT directly mutate PrintJob state. It does NOT create EpistemicRecords; that is the responsibility of the Epistemic Subsystem. If an observation requires a state transition, the Observation Engine produces an application-level input that Job Manager validates and applies.

## 15. Epistemic Subsystem

The Epistemic Subsystem is responsible for:

- epistemic qualification
- freshness evaluation
- consistency evaluation
- reconciliation
- EpistemicRecord creation

It must NOT directly mutate PrintJob state or authorize execution.

## 16. Event semantics

### Event identity

```text
event_id: UUID v7
event_type: string
schema_version: semver
aggregate_id: string
aggregate_type: string
producer: component identifier
timestamp: ISO-8601
correlation_id: UUID | null
causation_id: UUID | null
trace_id: UUID
idempotency_key: event_id
tenant_id: reserved
```

### Delivery semantics

PrintForge uses at-least-once delivery with idempotent consumers.

- at-least-once delivery
- duplicate handling via event_id idempotency
- replay semantics: events may be replayed from store
- dead-letter behavior: undeliverable events move to dead-letter queue

## 17. External dependency mapping

| Dependency | Responsibility |
|------------|----------------|
| PostgreSQL | job metadata, domain state, provenance, event metadata |
| S3/object storage | document spool artifacts, rendered artifacts, archival artifacts |
| Kafka | asynchronous event transport |
| KMS | encryption keys, protected artifact/data encryption |

None of these are required in the local Docker development baseline unless already necessary.

## 18. Operational architecture

### Non-functional requirements

| Property | Requirement |
|----------|-------------|
| Determinism | State transitions and routing decisions are reproducible |
| Reliability | Failures are isolated; no cascading domain corruption |
| Availability | Provider failures degrade gracefully |
| Latency | TBD — deployment-profile-specific; not an architectural contradiction |
| Throughput | TBD — deployment-profile-specific; not an architectural contradiction |
| Idempotency | All mutating operations are idempotent with respect to idempotency keys |
| Backpressure | Queue depth limits and circuit breakers prevent resource exhaustion |
| Retention | Job and document retention governed by retention policies |
| Disaster recovery | TBD — deployment-profile-specific; not an architectural contradiction |
| Observability | Structured logs, metrics, distributed tracing |
| Security | Authentication, authorization, encryption, audit logging |
| Auditability | Append-only audit trail with immutable provenance chains |
| Compatibility | IPP 2.0+ as canonical internal representation |
| Upgrade/migration | Versioned APIs and event schemas; backward-compatible transitions |

## 19. Trust boundaries

| Component | Trust level |
|-----------|-------------|
| User | External — authenticated but untrusted input |
| API | Trust boundary that authenticates, validates, and constrains untrusted external input |
| Application | Trusted — internal application services |
| Domain | Trusted — deterministic core |
| Provider | Partially trusted — executes under contract, may fail |
| Printer | External — authoritative for physical state only |
| Epistemic subsystem | Trusted advisory — never mutates production state |
| Persistence | Trusted — data store, access controlled |
| Object storage | Trusted — encrypted at rest, access controlled |
| Event infrastructure | Trusted — at-least-once delivery, idempotent consumers |

## 20. Key components

- **Job Manager**: Accepts jobs, validates, routes, and tracks state. Sole writer of PrintJob lifecycle state. May request execution via provider contract.
- **Scheduler**: Queues jobs, selects printers, dispatches to providers. Produces SchedulingDecision.
- **Policy Engine**: Evaluates authorization, constraints, and routing restrictions. Produces PolicyDecision.
- **Provider Registry**: Discovers and manages provider plugins. Tracks provider health and capabilities.
- **Spool**: Persists documents and job metadata.
- **Event Bus**: Emits and consumes domain events.
- **Observation Engine**: Ingests provider observations, normalizes, preserves raw evidence and provenance, forwards evidence for epistemic evaluation. Does not mutate PrintJob state. Does not create EpistemicRecords.
- **Epistemic Subsystem**: Qualifies observations with freshness, staleness, and consistency status. Creates EpistemicRecords. Advisory only.

## 21. References

- PRINTFORGE_SYSTEM_CONTRACT.md
- DETERMINISM_CONTRACT.md
- SIMULATOR_CONTRACT.md
- FAILURE_CONTRACT.md
- EVENT_CONTRACT.md
- SECURITY_CONTRACT.md
- SPOOL_CONTRACT.md
- DOCUMENT_CONTRACT.md
- PROVENANCE_CONTRACT.md
- PROVIDER_CONTRACT.md
- All contract documents in docs/contracts/
- All ADRs in docs/adr/
