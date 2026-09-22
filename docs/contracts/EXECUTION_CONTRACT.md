# Execution Contract

## 1. PrintExecution Object

`PrintExecution` represents the runtime execution record of a PrintJob on a specific printer.

```yaml
PrintExecution:
  execution_id: string (UUID v7, immutable)
  job_id: string (immutable)
  printer_id: string (immutable)
  provider_id: string (immutable)
  started_at: timestamp (immutable)
  completed_at: timestamp | null (mutable)
  state: ExecutionState (mutable)
  result: ExecutionResult | null (mutable)
  error: ExecutionError | null (mutable)
  metrics: ExecutionMetrics (mutable, append-only)
  retry_count: integer (>=0, mutable)
  parent_execution_id: string | null (immutable, for retries)
  trace: TraceContext (immutable)
```

### Fields

- **execution_id**: Unique execution identifier. Immutable.
- **job_id**: References the PrintJob.
- **printer_id**: The printer executing the job.
- **provider_id**: The provider controlling the printer.
- **started_at**: When execution began.
- **completed_at**: When execution ended. Null if still running.
- **state**: Current execution state.
- **result**: Success or failure result.
- **error**: Error details if failed.
- **metrics**: Execution metrics (see below).
- **retry_count**: Number of retry attempts. 0 for first execution.
- **parent_execution_id**: For retries, references the previous execution.
- **trace**: Distributed trace context captured at execution start.

## 2. ExecutionState Enum

| Value | Description |
|-------|-------------|
| RUNNING | Execution is in progress. |
| SUCCEEDED | Execution completed successfully. |
| FAILED | Execution failed. |
| CANCELLED | Execution was cancelled. |
| TIMEOUT | Execution exceeded timeout. |

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

1. **Dispatch**: The system selects a printer and provider. Creates a `PrintExecution` with state `RUNNING`.
2. **Start**: Provider confirms execution started. `started_at` is set.
3. **Progress**: Provider may send progress updates (see EVENT_CONTRACT.md).
4. **Completion**: Provider reports final state.
   - `SUCCEEDED`: `result` is populated, `completed_at` is set.
   - `FAILED`: `error` is populated, `completed_at` is set.
   - `CANCELLED`: Execution was cancelled, `completed_at` is set.
   - `TIMEOUT`: System timeout triggered, `error` is populated.
5. **Post-Processing**: Metrics are finalized, job state transitions to terminal.

## 7. Timeout Behavior

- Each execution has a configurable timeout (see PROVIDER_CONTRACT.md).
- If the provider does not report completion within the timeout, the system transitions the execution to `TIMEOUT`.
- Timeout is not retryable by default. The job fails unless retry policy explicitly allows timeout retries.

## 8. Retry Semantics

- Retries create a new `PrintExecution` with a new `execution_id`.
- `parent_execution_id` links to the failed execution.
- `retry_count` is incremented.
- The same `job_id` and `printer_id` may be used, or a different printer may be selected.
- Retry policy is defined per job or globally (see FAILURE_CONTRACT.md).

## 9. Cancellation

- Cancellation is requested by transitioning the job to `CANCELLING`.
- The provider is notified asynchronously.
- If the provider confirms cancellation, execution state becomes `CANCELLED`.
- If the provider reports completion before acknowledging cancellation, execution state becomes `SUCCEEDED` and the cancellation is logged but not applied.

## 10. Idempotency

- The same `execution_id` must never be reused.
- Provider must be idempotent with respect to `job_id` and `execution_id`.
- If a provider receives a duplicate start request with the same `execution_id`, it must return the current state without re-executing.
