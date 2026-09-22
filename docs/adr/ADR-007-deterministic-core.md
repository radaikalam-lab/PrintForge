# ADR-007: Deterministic Core

## Status

Accepted

## Context

PrintForge must be reliable, testable, and debuggable. Non-deterministic behavior makes these goals difficult:

- Flaky tests erode confidence in the codebase.
- Reproducing production bugs requires capturing the exact non-deterministic state.
- Simulation results cannot be compared or repeated.
- Formal verification and property-based testing are impossible on non-deterministic code.

We need a strategy to maximize determinism in the core while accommodating necessary non-determinism (time, randomness, I/O).

## Decision

We adopt a "deterministic core" architecture:

1. **Pure Core**: The core business logic (validation, routing, state transitions, policy evaluation) is implemented as pure, deterministic functions.
2. **Side-Effect Boundary**: All side effects (I/O, time, randomness) are pushed to the edges of the system.
3. **Injectable Dependencies**: Time, randomness, and external state are injected as dependencies, never hardcoded.
4. **Deterministic Mode**: The system can run in a fully deterministic mode for testing and simulation.
5. **Property-Based Testing**: The deterministic core is verified using property-based testing.

### Pure Core

The core consists of:
- `validate_job(job, capabilities) -> ValidationResult`
- `match_capabilities(requirement, capabilities) -> MatchResult`
- `route_job(job, printers) -> RouterDecision`
- `validate_job_transition(current_state, new_state) -> None` (raises `ValueError` on invalid transition)
- `evaluate_policy(policy, context) -> PolicyResult`

These functions:
- Have no side effects.
- Depend only on their inputs.
- Return identical results for identical inputs.

### Side-Effect Boundary

Side effects are handled by adapters:
- `Clock` adapter: provides current time.
- `Random` adapter: provides random numbers.
- `Spool` adapter: reads and writes data.
- `Provider` adapter: communicates with printers.

The core never calls these adapters directly. They are injected at the application layer.

### Deterministic Mode

In deterministic mode:
- `Clock` returns a fixed, incrementing timestamp.
- `Random` uses a fixed seed.
- `Spool` reads from a pre-loaded in-memory snapshot.
- `Provider` returns pre-configured responses.

### Property-Based Testing

- The core is tested with property-based frameworks (e.g., QuickCheck, Hypothesis).
- Properties include:
  - `transition_state` is total (every valid input produces a valid output).
  - `match_capabilities` is reflexive and symmetric.
  - `route_job` always returns a printer from the input set.

## Consequences

### Positive

- Tests are reliable and repeatable.
- Bugs are easier to reproduce.
- Simulation results are comparable.
- The core is easier to reason about and formally verify.

### Negative

- Pure functional style may be unfamiliar to some developers.
- Injecting dependencies adds boilerplate.
- Debugging pure functions may be less intuitive for developers used to imperative code.

### Neutral

- The side-effect boundary enforces clean architecture.
- Deterministic mode is a first-class feature, not an afterthought.

## References

- PRINTFORGE_SYSTEM_CONTRACT.md
- DETERMINISM_CONTRACT.md
- SIMULATOR_CONTRACT.md
