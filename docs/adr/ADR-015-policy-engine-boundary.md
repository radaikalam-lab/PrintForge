# ADR-015: Policy Engine Boundary

## Status

Accepted

## Context

PrintForge needs a component that evaluates authorization, constraints, and routing restrictions before jobs are executed. This component must not execute physical operations or mutate domain state.

## Decision

The Policy Engine is an application-layer component that produces PolicyDecision objects. It does not execute physical operations.

Responsibilities:
- authorization
- constraints
- capability requirements
- operational limits
- routing restrictions
- data handling restrictions

Policy evaluation produces a decision. Policy evaluation itself does not execute physical operations. The Job Manager enforces the resulting transitions.

The Policy Engine may:
- query read-only repositories
- evaluate policies against job and printer context
- emit PolicyDecision objects

The Policy Engine may not:
- mutate PrintJob state
- invoke providers
- execute printer operations
- bypass validation

## Consequences

### Positive

- Policy logic is centralized and testable.
- Policy decisions are explicit and auditable.
- The Job Manager enforces transitions, preserving the single-writer rule.

### Negative

- Policy evaluation adds latency to the job lifecycle.
- Complex policies may require tuning.

### Neutral

- This is a standard policy enforcement point pattern.
- The Policy Engine can be extended without changing the Job Manager.

## Alternatives Considered

1. **Inline policy checks**: Policy logic scattered across services. Rejected because it is hard to test and audit.
2. **Provider-enforced policy**: Providers enforce policy. Rejected because providers are external and may not share the same policy context.

## References

- PRINTFORGE_SYSTEM_CONTRACT.md
- ARCHITECTURE.md
