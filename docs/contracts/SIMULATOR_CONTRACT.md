# Simulator Contract

## 1. Simulator Purpose

The simulator is a test double that implements the Provider interface without requiring physical hardware. It is used for development, testing, and CI/CD.

## 2. Simulator Interface

The simulator must implement the same `Provider` interface defined in PROVIDER_CONTRACT.md.

```yaml
Simulator:
  provider_id: string (UUID v7)
  name: string (e.g., "Simulated IPP Provider")
  type: "SIMULATOR"
  version: string (semver)
  capabilities: ProviderCapabilityDeclaration[]
  config: SimulatorConfig
  status: ProviderStatus
  registered_at: timestamp
  last_heartbeat: timestamp
  metadata: map<string, string>
  trace: TraceContext
```

## 3. SimulatorConfig

```yaml
SimulatorConfig:
  printers: PrinterConfig[]
  failure_rate: float [0.0..1.0]
  latency_min_ms: integer (>=0)
  latency_max_ms: integer (>=0)
  deterministic: boolean
  seed: integer | null
```

### PrinterConfig

```yaml
PrinterConfig:
  printer_id: string (UUID v7)
  name: string
  capabilities: PrinterCapabilities
  status: PrinterStatus
  health: PrinterHealth
  metrics: SimulatedMetrics
```

### SimulatedMetrics

```yaml
SimulatedMetrics:
  queue_length: integer (>=0)
  current_job_id: string | null
  pages_printed: integer (>=0)
  toner_level: [black: 0..1, cyan: 0..1, magenta: 0..1, yellow: 0..1] | null
  paper_level: [tray1: 0..1, ...] | null
```

## 4. Simulator Requirements

1. **Interface Compliance**: The simulator must implement all provider interfaces exactly.
2. **Deterministic Mode**: When `deterministic: true`, the simulator must produce identical results for identical inputs.
3. **Configurable Failure**: The simulator must be able to simulate failures at configurable rates.
4. **Configurable Latency**: The simulator must simulate network latency between `latency_min_ms` and `latency_max_ms`.
5. **Stateful Simulation**: The simulator must maintain internal state (queue, current job, metrics) across calls.
6. **Observation Generation**: The simulator must generate `PrinterObservation` objects on demand or on a schedule.

## 5. Simulator Behavior

### Job Execution

- When the simulator receives a job execution request, it must:
  1. Transition the printer to BUSY.
  2. Simulate processing time (configurable, default: 1-5 seconds).
  3. Simulate success or failure based on `failure_rate`.
  4. Update metrics (pages printed, toner levels, etc.).
  5. Transition the printer back to IDLE.
  6. Emit appropriate events.

### Observations

- The simulator must emit observations on a configurable interval (default: 5 seconds).
- Observations must reflect the simulator's internal state.
- Observations must include simulated metrics.

### Failures

- The simulator must be able to simulate:
  - Transient failures (timeouts, temporary unavailability)
  - Permanent failures (hardware failure, out of paper)
  - Partial failures (some pages printed, then error)
- Failure simulation must be controllable per printer or globally.

## 6. Determinism

- In deterministic mode, the simulator must use a seeded PRNG.
- The seed must be configurable and recorded in simulation reports.
- Running the same simulation with the same seed must produce identical results.

## 7. Simulator Events

The simulator must emit all provider lifecycle events (see EVENT_CONTRACT.md):
- `ProviderRegistered`
- `ProviderStatusChanged`
- `PrinterRegistered`
- `PrinterStatusChanged`
- `ExecutionStarted`
- `ExecutionCompleted`
- `ExecutionFailed`
- `ObservationReceived`

## 8. Testing Integration

- The simulator must be usable as a drop-in replacement for real providers in tests.
- The simulator must not require external dependencies.
- The simulator must be configurable via environment variables or config files.
