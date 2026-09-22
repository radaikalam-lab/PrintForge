# ADR-004: Provider Isolation

## Status

Accepted

## Context

Providers are external adapters that may fail, hang, or behave unexpectedly. Without isolation, a provider failure can corrupt domain state, bypass policy, or destabilize the core system.

## Decision

Providers are adapters between PrintForge ports and external systems. They run behind well-defined interfaces and must enter the application through explicit contracts.

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

Provider output enters the application through explicit contracts (e.g., ExecutionResult, PrinterObservation).

## Consequences

### Positive

- Provider failures are isolated to the provider boundary.
- The core never trusts provider output without validation.
- New providers can be added without modifying core logic.

### Negative

- Provider failures must be explicitly handled (circuit breakers, timeouts).
- More boilerplate for provider contracts.

### Neutral

- This is a standard ports-and-adapters pattern.
- The simulator provider implements the same interface as real providers.

## Alternatives Considered

1. **Tight coupling**: Providers could directly mutate domain objects. Rejected because it breaks testability and isolation.
2. **Shared state**: Providers could share state with the core. Rejected because it creates hidden coupling.

## References

- PRINTFORGE_SYSTEM_CONTRACT.md
- PROVIDER_CONTRACT.md
- SIMULATOR_CONTRACT.md
