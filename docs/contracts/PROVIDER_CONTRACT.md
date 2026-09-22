# Provider Contract

## 1. Provider Interface

A `Provider` is the component responsible for translating PrintForge execution requests into printer-specific commands.

```yaml
Provider:
  provider_id: string (UUID v7, immutable)
  name: string (immutable)
  type: ProviderType (immutable)
  version: string (semver, immutable)
  capabilities: ProviderCapabilityDeclaration[] (immutable)
  config: ProviderConfig (encrypted at rest)
  status: ProviderStatus (mutable)
  registered_at: timestamp (immutable)
  last_heartbeat: timestamp (mutable)
  metadata: map<string, string> (mutable)
  trace: TraceContext (mutable, append-only)
```

### Fields

- **provider_id**: Unique identifier. Immutable.
- **name**: Human-readable name.
- **type**: The provider type (e.g., `IPP`, `CUPS`, `PAPPL`, `SIMULATOR`).
- **version**: Provider implementation version.
- **capabilities**: Declared capability support (see below).
- **config**: Provider-specific configuration (e.g., IPP endpoint, CUPS server). Encrypted at rest.
- **status**: Current provider status (see Status Enum).
- **registered_at**: Registration timestamp.
- **last_heartbeat**: Last successful health check.
- **metadata**: Key-value pairs.
- **trace**: Distributed trace context.

## 2. ProviderType Enum

| Value | Description |
|-------|-------------|
| IPP | Internet Printing Protocol provider. |
| CUPS | Common UNIX Printing System provider. |
| PAPPL | Printer Application provider. |
| SIMULATOR | Simulated provider for testing. |
| CUSTOM | Custom provider implementation. |

## 3. ProviderStatus Enum

| Value | Description |
|-------|-------------|
| ONLINE | Provider is operational. |
| DEGRADED | Provider is operational but experiencing issues. |
| OFFLINE | Provider is unreachable. |
| ERROR | Provider has encountered a fatal error. |

## 4. ProviderCapabilityDeclaration

```yaml
ProviderCapabilityDeclaration:
  capability_type: string (e.g., "color", "duplex", "media_type")
  supported: boolean
  details: map<string, any>
```

## 5. Capability Declarations

Providers must declare their supported capabilities at registration time. The system uses these declarations to:
- Validate printer capability claims.
- Determine which providers can handle which job types.
- Enable capability-based routing.

Providers must not declare capabilities they do not actually support. False declarations are a security violation (see SECURITY_CONTRACT.md).

## 6. Failure Semantics

- **Provider-Level Failure**: If a provider becomes OFFLINE or ERROR, all printers managed by that provider transition to OFFLINE.
- **Printer-Level Failure**: If a printer reports an error, only that printer transitions to ERROR. Other printers on the same provider remain unaffected.
- **Transient vs. Permanent**: Providers must classify errors as transient (retryable) or permanent (non-retryable).

## 7. Timeout Behavior

- Providers must define and honor a `request_timeout` for all operations.
- If a provider does not respond within `request_timeout`, the system treats it as a timeout failure.
- Timeout failures are transient by default but may be configured per job.

## 8. Retry Semantics

- Providers must implement retry logic for transient failures.
- Retry policy: exponential backoff with jitter, max 3 retries, base delay 1 second.
- Providers must be idempotent: retrying the same request with the same `execution_id` must not cause duplicate side effects.
- The system may also implement retries independent of the provider (see FAILURE_CONTRACT.md).

## 9. Idempotency Semantics

- All provider APIs must accept an `Idempotency-Key` header (or equivalent).
- The provider must store idempotency keys for at least 24 hours.
- Duplicate requests with the same idempotency key must return the same result.
- Providers must not expose internal state through idempotency key storage.

## 10. Health Checks

- Providers must implement a health check endpoint or mechanism.
- The system polls health checks at a configurable interval (default: 30 seconds).
- Failed health checks transition the provider to DEGRADED after 2 consecutive failures, and OFFLINE after 3 consecutive failures.

## 11. Observability

- Providers must emit structured logs compatible with the system's trace context.
- Providers must expose metrics for: request latency, error rate, queue depth, and throughput.
- Providers must emit lifecycle events (see EVENT_CONTRACT.md).
