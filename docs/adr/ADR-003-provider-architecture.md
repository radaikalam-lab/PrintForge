# ADR-003: Provider Architecture

## Status

Accepted

## Context

PrintForge must support multiple printer types, protocols, and deployment environments. We need an architecture that:
- Isolates printer-specific logic.
- Enables independent evolution of provider implementations.
- Supports testing without physical hardware.
- Allows users to add custom providers without modifying the core.

## Decision

We adopt a plugin-based provider architecture with a well-defined interface:

1. **Provider Interface**: A stable, versioned interface that all providers must implement.
2. **Plugin Loading**: Providers are loaded dynamically at runtime via plugins.
3. **Capability Declaration**: Providers declare their supported capabilities at registration time.
4. **Health Monitoring**: The core monitors provider health and isolates failures.
5. **Simulator Provider**: A built-in provider for testing and development.

### Provider Interface

The Provider interface includes:
- `register_printer(printer_config) -> Printer`
- `unregister_printer(printer_id) -> void`
- `execute_job(execution) -> ExecutionResult`
- `cancel_job(execution_id) -> CancellationResult`
- `observe_printer(printer_id) -> PrinterObservation`
- `health_check() -> HealthStatus`

### Plugin Loading

- Providers are packaged as shared libraries or containers.
- The core loads providers via a plugin registry.
- Provider configuration is injected at load time.
- Providers run in separate processes or containers for isolation.

### Failure Isolation

- Provider failures must not crash the core.
- The core uses circuit breakers and timeouts to isolate provider failures.
- Failed providers are marked OFFLINE. Their printers are marked OFFLINE.
- The core continues operating with remaining providers.

### Simulator Provider

- The simulator implements the Provider interface.
- It generates synthetic observations and execution results.
- It supports configurable latency, failure rates, and deterministic mode.
- It is used for unit tests, integration tests, and development.

## Consequences

### Positive

- The core is decoupled from printer-specific logic.
- New providers can be added without modifying the core.
- Testing is simplified with the simulator provider.
- Failure isolation improves system resilience.

### Negative

- Plugin loading adds complexity to deployment and configuration.
- Cross-provider features (e.g., global job routing across CUPS and PAPPL) require careful design.
- Debugging provider failures may be harder due to process boundaries.

### Neutral

- The Provider interface is versioned. Breaking changes require a new major version.
- Providers may be implemented in any language that supports the plugin interface (e.g., gRPC, shared library).

## References

- PRINTFORGE_SYSTEM_CONTRACT.md
- PROVIDER_CONTRACT.md
- SIMULATOR_CONTRACT.md
