# PrintForge System Contract

## 1. System Boundary

PrintForge is a print job orchestration and execution platform. The system boundary encompasses:

- **Intent Layer**: Print job definitions, document payloads, and routing policies.
- **Validation Layer**: Capability matching, policy enforcement, and pre-execution checks.
- **Execution Layer**: Job dispatch, provider interaction, and print execution.
- **Observation Layer**: Printer telemetry, job status, and event emission.

PrintForge does **not** include:
- Physical printer hardware interfaces.
- Direct user-facing GUI applications (unless explicitly integrated).
- Operating system print spoolers.

## 2. Architectural Laws

The following laws are non-negotiable:

1. **Separation of Concerns**: Intent, validation, execution, and observation must remain in distinct modules with unidirectional data flow.
2. **Deterministic Core**: All job state transitions, routing decisions, and validation results must be reproducible from immutable inputs.
3. **Provider Isolation**: Provider implementations must not share state with the core system. Failure in one provider must not corrupt another.
4. **Capability-Driven Execution**: No job may execute on a printer unless the printer's declared capabilities satisfy the job's requirements.
5. **Observable Authority**: The system may observe but must not directly control physical printer hardware. Control is delegated exclusively to providers.
6. **Immutable Provenance**: Every state change, event, and observation must carry a cryptographic or logical provenance chain.
7. **Contractual Integrity**: All public interfaces, APIs, and events are governed by the contracts defined in this document set. Breaking changes require versioned API evolution.

## 3. Design Philosophy

PrintForge follows these principles:

- **Convention over Configuration**: Sensible defaults for spooling, retries, and timeouts.
- **Explicit over Implicit**: All state transitions, capability requirements, and failure modes are explicitly defined.
- **Composability**: Providers, spool backends, and observation sinks are pluggable.
- **Testability**: The deterministic core enables property-based testing and simulation-first development.
- **Simulation-First**: All features must be verifiable through simulation before physical hardware integration.

## 4. Deployment Constraints

- PrintForge must run on Linux containers (Docker or compatible).
- All I/O with external systems must be async and cancellable.
- The system must not require root privileges for normal operation.
- Secrets and credentials must be injected via environment or secret management, never hardcoded.
- All network-facing endpoints must use TLS.
- The system must be deployable as a single binary with embedded configuration or as a distributed service.

## 5. Normative References

All other contract documents in `docs/contracts/` are normative extensions of this system contract. In case of conflict, the more specific contract takes precedence.
