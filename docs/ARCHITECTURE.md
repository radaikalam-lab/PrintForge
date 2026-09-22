# Architecture

## 1. Overview

PrintForge is a print job orchestration and execution platform. It separates intent (what to print), validation (can it be printed), execution (printing it), and observation (what happened).

## 2. System Boundaries

PrintForge does not include physical printer hardware, GUI applications, or OS print spoolers. See PRINTFORGE_SYSTEM_CONTRACT.md for details.

## 3. Architectural Laws

1. Separation of concerns: intent, validation, execution, and observation are distinct layers.
2. Deterministic core: state transitions and routing decisions are reproducible.
3. Provider isolation: provider failures do not corrupt the core.
4. Capability-driven execution: jobs only execute on capable printers.
5. Observable authority: the system observes but does not directly control printers.
6. Immutable provenance: every state change carries a provenance chain.
7. Contractual integrity: public interfaces are governed by contracts.

## 4. Layer Structure

```
+--------------------------------------------------+
|                  API Layer                        |
|         (Versioned REST/GraphQL)                  |
+--------------------------------------------------+
|               Application Layer                   |
|     (Job management, routing, policy)             |
+--------------------------------------------------+
|                  Core Layer                       |
|   (Validation, state machine, determinism)        |
+--------------------------------------------------+
|               Provider Layer                      |
|     (IPP, CUPS, PAPPL, Simulator plugins)         |
+--------------------------------------------------+
|               Spool Layer                         |
|     (Document and metadata persistence)           |
+--------------------------------------------------+
|               Event Bus                           |
|     (Domain events, observability)                |
+--------------------------------------------------+
```

## 5. Key Components

- **API Gateway**: Versioned API endpoints, authentication, rate limiting.
- **Job Manager**: Accepts jobs, validates, routes, and tracks state.
- **Scheduler**: Queues jobs, selects printers, dispatches to providers.
- **Provider Registry**: Discovers and manages provider plugins.
- **Spool**: Persists documents and job metadata.
- **Event Bus**: Emits and consumes domain events.
- **Observation Engine**: Reconciles provider observations with authoritative state.

## 5a. Epistemic Architecture

```
+--------------------------------------------------+
|                  API Layer                        |
|         (Versioned REST/GraphQL)                  |
+--------------------------------------------------+
|               Application Layer                   |
|     (Job management, routing, policy)             |
+--------------------------------------------------+
|                  Core Layer                       |
|   (Validation, state machine, determinism)        |
+--------------------------------------------------+
|           Epistemic Boundary Layer                 |
|  +--------------------------------------------+  |
|  |  Observed / Declared / Derived / Assumed    |  |
|  |  Status only. Never executes operations.    |  |
|  +--------------------------------------------+  |
+--------------------------------------------------+
|               Provider Layer                      |
|     (IPP, CUPS, PAPPL, Simulator plugins)         |
+--------------------------------------------------+
```

### 5a.1 Epistemic Novelty ≠ Production Authority

Observations, declarations, and derived signals carry **epistemic status** (e.g., `OBSERVED`, `DECLARED`, `ASSUMED`, `STALE`, `CONTRADICTED`). They inform control-plane decisions but **never execute printer operations or bypass validation**. Only explicit application services and authorized provider interfaces may mutate domain state.

## 6. Data Flow

1. Client uploads document and creates PrintJob via API.
2. Job Manager validates job and capabilities.
3. Scheduler routes job to an eligible printer.
4. Provider executes the job on the printer.
5. Provider reports progress and completion via events and observations.
6. Observation Engine reconciles observations with authoritative state.
7. Job Manager transitions job to terminal state.
8. Events are emitted and stored for audit and debugging.

## 7. Deployment Model

- Linux containers (Docker) on Kubernetes.
- Single binary per container.
- Sidecars for logging, metrics, and tracing.
- External dependencies: PostgreSQL, Kafka, S3, KMS.

## 8. Cross-Cutting Concerns

- **Security**: Authentication, authorization, encryption, audit logging (see SECURITY_CONTRACT.md).
- **Observability**: Structured logs, metrics, distributed tracing (see EVENT_CONTRACT.md).
- **Resilience**: Circuit breakers, retries, timeouts, graceful degradation (see FAILURE_CONTRACT.md).
- **Testing**: Simulation-first, property-based tests, deterministic mode (see DETERMINISM_CONTRACT.md and SIMULATOR_CONTRACT.md).

## 9. Extension Points

- **Providers**: Add new printer protocols by implementing the Provider interface.
- **Spool Backends**: Add new storage backends by implementing the Spool interface.
- **Event Handlers**: Add new event consumers by subscribing to the Event Bus.
- **Policies**: Add new routing and validation policies via the Policy Engine.

## 10. References

- PRINTFORGE_SYSTEM_CONTRACT.md
- All contract documents in docs/contracts/
- All ADRs in docs/adr/
