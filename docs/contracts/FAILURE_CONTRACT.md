# Failure Contract

## 1. Failure Isolation Principle

Failures must be isolated to the smallest possible scope. A failure in one component must not corrupt or destabilize unrelated components.

## 2. Failure Domains

| Domain | Isolation Boundary | Blast Radius |
|--------|-------------------|--------------|
| Provider | Process or container | All printers on that provider |
| Printer | Logical within provider | Single job execution |
| Spool Backend | Process or service | All jobs and documents |
| API Server | Process or container | API requests during outage |
| Event Bus | Infrastructure | Event delivery delays |

## 3. Failure Semantics

### Retryable Failures

| Failure | Retryable | Reason |
|---------|-----------|--------|
| Network timeout | Yes | Transient network condition |
| Provider temporarily unavailable | Yes | Provider may recover |
| Printer busy (if job allows queueing) | Yes | Temporary resource contention |
| Rate limit | Yes | Transient throttling |

### Non-Retryable Failures

| Failure | Retryable | Reason |
|---------|-----------|--------|
| Invalid job definition | No | Client error |
| Capability mismatch | No | Configuration error |
| Document not found | No | Data integrity issue |
| Authentication failure | No | Security violation |
| Permission denied | No | Security violation |
| Document too large | No | Client error |
| Unsupported format | No | Client error |

## 4. Retry Policy

```yaml
RetryPolicy:
  max_retries: integer (default: 3)
  base_delay_ms: integer (default: 1000)
  max_delay_ms: integer (default: 30000)
  backoff_multiplier: float (default: 2.0)
  jitter: boolean (default: true)
  retryable_codes: string[]
```

### Retry Rules

1. Retries must use exponential backoff with jitter.
2. Retries must not exceed `max_retries`.
3. Retries must not exceed `job.max_retries` if set.
4. Retries must preserve the original `job_id` and `trace_id`.
5. Retries must emit `JobRetried` events.

## 5. Circuit Breaker

- Providers must implement circuit breakers.
- Circuit breaker states: CLOSED, OPEN, HALF_OPEN.
- Circuit opens after `failure_threshold` consecutive failures (default: 5).
- Circuit half-opens after `recovery_timeout` (default: 30s).
- If the half-open probe succeeds, circuit closes. If it fails, circuit reopens.

## 6. Timeout Behavior

- All provider operations must have timeouts.
- Default provider timeout: 30 seconds.
- Default job queue timeout: 5 minutes.
- Timeouts must be configurable per job, per provider, and globally.
- Timeout failures are retryable by default.

## 7. Graceful Degradation

- If a provider fails, the system must attempt to route to alternative providers.
- If no alternative provider is available, the job must fail with a clear error.
- The system must never deadlock waiting for a failed provider.

## 8. Failure Recovery

- Recovered providers must re-register their printers.
- Recovered printers must be validated before receiving new jobs.
- Jobs that failed due to provider failure may be retried automatically if the retry policy permits.

## 9. Monitoring and Alerting

- The system must emit `ProviderStatusChanged` and `PrinterStatusChanged` events on failures.
- The system must expose metrics for: failure rate, retry rate, timeout rate, circuit breaker state.
- Alerts must fire when failure rates exceed thresholds.
