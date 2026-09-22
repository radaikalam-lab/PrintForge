# Printer Contract

## 1. Printer Object

A `Printer` represents a registered, routable printing destination within PrintForge.

```yaml
Printer:
  printer_id: string (UUID v7, immutable)
  name: string (immutable)
  provider_id: string (immutable)
  capabilities: PrinterCapabilities (immutable, versioned)
  status: PrinterStatus (mutable)
  location: string | null (mutable)
  metadata: map<string, string> (mutable, validated)
  registered_at: timestamp (immutable)
  last_seen: timestamp (mutable)
  health: PrinterHealth (mutable)
  trace: TraceContext (mutable, append-only)
```

### Fields

- **printer_id**: Unique identifier for the printer. Immutable after registration.
- **name**: Human-readable name. Must be unique within the same provider.
- **provider_id**: References the provider managing this printer. Immutable.
- **capabilities**: Declared capabilities (see CAPABILITY_CONTRACT.md). Immutable after registration. Versioned if capabilities change.
- **status**: Current operational status (see Status Enum).
- **location**: Physical or logical location. Null if unknown.
- **metadata**: Key-value pairs. Keys must match `^[a-z0-9_-]+$`.
- **registered_at**: Timestamp of registration.
- **last_seen**: Last time the provider reported this printer as reachable.
- **health**: Health indicator (see Health Enum).
- **trace**: Distributed trace context.

## 2. Status Enum

| Value | Description |
|-------|-------------|
| IDLE | Printer is registered and available. |
| BUSY | Printer is executing a job. |
| ERROR | Printer reported an error condition. |
| OFFLINE | Provider reports printer unreachable. |
| MAINTENANCE | Printer is intentionally unavailable. |
| DECOMMISSIONED | Printer is no longer in service. |

## 3. Health Enum

| Value | Description |
|-------|-------------|
| HEALTHY | Operational within declared capabilities. |
| DEGRADED | Operational but with warnings (e.g., low toner). |
| UNHEALTHY | Not operational or capabilities degraded. |
| UNKNOWN | Provider has not reported health. |

## 4. Registration and Lifecycle

1. **Registration**: A provider registers a printer. The system assigns `printer_id`. Capabilities are validated against the provider's declared capability schema.
2. **Heartbeat**: The provider must update `last_seen` at least every 60 seconds. Failure results in transition to OFFLINE.
3. **Capability Updates**: Capabilities are immutable on the Printer object. To update capabilities, the printer must be deregistered and re-registered with a new `printer_id`.
4. **Decommissioning**: A printer may be marked DECOMMISSIONED. No new jobs may be routed to it. Existing jobs must complete or be cancelled.

## 5. Routing Eligibility

A printer is eligible for job routing if and only if:
- `status` is IDLE or BUSY (if the job allows concurrent execution).
- `health` is HEALTHY or DEGRADED.
- `last_seen` is within the provider's heartbeat timeout.
- The printer's capabilities satisfy the job's `target_capabilities` (see CAPABILITY_CONTRACT.md).

## 6. Observability

Every status or health transition emits a `PrinterStatusChanged` event (see EVENT_CONTRACT.md). The event must include:
- `printer_id`
- `from_status`
- `to_status`
- `timestamp`
- `trace_id`
