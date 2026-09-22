# Execution Contract

## 1. PrintExecution Object

`PrintExecution` represents an individual provider/device execution attempt for a PrintJob.

```yaml
PrintExecution:
  execution_id: string (UUID v7, immutable)
  job_id: string (immutable)
  printer_id: string (immutable)
  provider: string | null (immutable)
  requested_operation: string (immutable)
  start_time: timestamp | null (mutable)
  end_time: timestamp | null (mutable)
  state: ExecutionState (mutable)
  result: ExecutionResult | null (mutable)
  failure_information: ExecutionError | null (mutable)
  metrics: ExecutionMetrics (mutable, append-only)
  attempt_number: integer (>=1, immutable)
  parent_execution_id: string | null (immutable, for retries)
  trace: TraceContext (immutable)
  provenance: map<string, any> (immutable)
```

### Fields

- **execution_id**: Unique execution identifier. Immutable.
- **job_id**: References the PrintJob.
- **printer_id**: The printer executing the attempt.
- **provider**: The provider controlling the printer.
- **requested_operation**: The operation requested (e.g., "submit").
- **start_time**: When execution began. Null if not started.
- **end_time**: When execution ended. Null if still running.
- **state**: Current execution state.
- **result**: Success or failure result.
- **failure_information**: Error details if failed.
- **metrics**: Execution metrics (see below).
- **attempt_number**: Sequence number of this attempt within the job. 1 for first attempt.
- **parent_execution_id**: For retries, references the previous attempt.
- **trace**: Distributed trace context captured at execution start.
- **provenance**: Immutable provenance chain for this attempt.

## 2. ExecutionState Enum

| Value | Description |
|-------|-------------|
| SUBMITTED | Provider accepted the attempt |
| PROCESSING | Provider is executing the attempt |
| COMPLETED | Attempt completed successfully |
| FAILED | Attempt failed |
| CANCELLED | Attempt was cancelled |
| REJECTED | Provider explicitly rejected the attempt before execution |
| UNKNOWN | Execution state is uncertain (e.g., provider lost connection) |

## 3. ExecutionResult Object

```yaml
ExecutionResult:
  success: boolean
  pages_printed: integer (>=0)
  impressions: integer (>=0)
  provider_data: map<string, any> (opaque)
```

## 4. ExecutionError Object

```yaml
ExecutionError:
  code: string
  message: string
  provider_error: map<string, any> | null
  retryable: boolean
  timestamp: timestamp
```

## 5. ExecutionMetrics Object

```yaml
ExecutionMetrics:
  setup_time_ms: integer (>=0)
  print_time_ms: integer (>=0)
  tear_down_time_ms: integer (>=0)
  total_time_ms: integer (>=0)
  bytes_sent: integer (>=0)
  bytes_received: integer (>=0)
```

## 6. Execution Lifecycle

1. **Dispatch**: The system selects a printer and provider. Creates a `PrintExecution` with state `SUBMITTED`.
2. **Start**: Provider confirms execution started. `started_at` is set, state becomes `PROCESSING`.
3. **Progress**: Provider may send progress updates (see EVENT_CONTRACT.md).
4. **Completion**: Provider reports final state.
   - `COMPLETED`: `result` is populated, `completed_at` is set.
   - `FAILED`: `failure_information` is populated, `completed_at` is set.
   - `CANCELLED`: Attempt was cancelled, `completed_at` is set.
   - `REJECTED`: Provider explicitly rejected the job before execution.
   - `UNKNOWN`: Provider connection lost; state is uncertain.
5. **Post-Processing**: Metrics are finalized. If retry is authorized, a new ExecutionAttempt is created.

## 7. Timeout Behavior

- Each execution attempt has a configurable timeout (see PROVIDER_CONTRACT.md).
- If the provider does not report completion within the timeout, the execution state becomes `UNKNOWN`.
- Timeout does not automatically declare physical failure.
- A subsequent observation or provider response may resolve the UNKNOWN state.

## 8. Retry Semantics

- Retries create a new `PrintExecution` with a new `execution_id`.
- `parent_execution_id` links to the previous attempt.
- `attempt_number` is incremented.
- The same `job_id` may be used, but a different `printer_id` may be selected.
- Retry policy is defined per job or globally (see FAILURE_CONTRACT.md).
- Retries must emit `JobRetried` events.

## 9. Cancellation

- Cancellation is requested by transitioning the PrintJob to `CANCELLING` (represented as CANCELLED in the current lifecycle).
- The provider is notified asynchronously.
- If the provider confirms cancellation, execution state becomes `CANCELLED`.
- If the provider reports completion before acknowledging cancellation, execution state becomes `COMPLETED` and the cancellation is logged but not applied.

## 10. Idempotency

- The same `execution_id` must never be reused.
- Provider must be idempotent with respect to `job_id` and `execution_id`.
- If a provider receives a duplicate start request with the same `execution_id`, it must return the current state without re-executing.
