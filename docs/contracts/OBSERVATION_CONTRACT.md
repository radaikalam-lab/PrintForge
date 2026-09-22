# Observation Contract

## 1. PrinterObservation Object

`PrinterObservation` represents a read-only telemetry snapshot from a provider about a printer.

```yaml
PrinterObservation:
  printer_id: string (UUID v7)
  observed_at: timestamp (immutable)
  status: PrinterStatus
  health: PrinterHealth
  capabilities: PrinterCapabilities | null
  metrics: PrinterMetrics
  alerts: Alert[]
  trace: TraceContext
```

### Fields

- **printer_id**: The printer being observed.
- **observed_at**: The time the observation was taken. Immutable.
- **status**: Reported operational status.
- **health**: Reported health indicator.
- **capabilities**: If the provider reports live capability verification, populated here. Null if not supported.
- **metrics**: Quantitative metrics (see below).
- **alerts**: Active alerts on the printer.
- **trace**: Distributed trace context.

## 2. PrinterMetrics

```yaml
PrinterMetrics:
  queue_length: integer (>=0)
  current_job_id: string | null
  pages_printed: integer (>=0)
  toner_level: [black: 0..1, cyan: 0..1, magenta: 0..1, yellow: 0..1] | null
  paper_level: [tray1: 0..1, tray2: 0..1, ...] | null
  temperature_c: number | null
  error_count: integer (>=0)
  uptime_seconds: integer (>=0)
```

## 3. Alert Object

```yaml
Alert:
  alert_id: string
  severity: "info" | "warning" | "error" | "critical"
  message: string
  code: string
  timestamp: timestamp
```

## 4. Observation vs. Authority

### Observation

- Observations are **read-only** reports from providers.
- The system must never send commands to printers via observations.
- Observations may be stale, delayed, or incomplete.
- The system must treat observations as untrusted input that requires validation.
- Each observation carries an `epistemic_status` field indicating its reliability (see OBSERVATION_EVIDENCE_CONTRACT.md).
- A `FreshnessPolicy` defines provider-specific thresholds for `FRESH`, `STALE`, and `EXPIRED` observations.

### Authority

- The system's internal state is the **authoritative** state.
- Observations may trigger state transitions only through defined reconciliation rules.
- If an observation contradicts authoritative state, the system must emit a `StateReconciliation` event and log the discrepancy.
- The system must never accept an observation that bypasses validation or security checks.
- Stale observations must not be treated as current physical truth.

## 5. Observation Semantics

1. **At-Least-Once**: Providers may send duplicate observations. The system must deduplicate using `(printer_id, observed_at)`.
2. **Out-of-Order**: Observations may arrive out of order. The system must process them in `observed_at` order.
3. **Gaps**: Missing observations are expected. The system must not assume a printer is offline based on a single missing observation.
4. **Timeout**: If no observation is received within the provider's heartbeat interval, the printer transitions to `OFFLINE`.

## 6. Reconciliation Rules

| Authoritative State | Observation | Action |
|---------------------|-------------|--------|
| IDLE | BUSY | Emit `PrinterBusy` event, update status |
| BUSY | IDLE | Emit `PrinterIdle` event, update status |
| IDLE | ERROR | Emit `PrinterError` event, mark DEGRADED |
| ERROR | IDLE | Emit `PrinterRecovered` event, mark HEALTHY if no other alerts |
| Any | OFFLINE | Emit `PrinterOffline` event, update status |
| OFFLINE | Any online state | Emit `PrinterOnline` event, update status |

## 7. Observability Requirements

- Every observation must be stored for at least 24 hours for debugging.
- Observations must be emitted as `ObservationReceived` events (see EVENT_CONTRACT.md).
- The system must expose a queryable observation history API (see API_CONTRACT.md).
