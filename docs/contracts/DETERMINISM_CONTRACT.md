# Determinism Contract

## 1. Deterministic Core Principle

The core of PrintForge must be fully deterministic: given identical inputs and system state, it must produce identical outputs.

## 2. Deterministic Components

The following components must be deterministic:

1. **Job Validation**: Given a `PrintJob` and a set of `PrinterCapabilities`, validation results must be identical.
2. **Capability Matching**: Given a `CapabilityRequirement` and `PrinterCapabilities`, the match result must be identical.
3. **Routing Decisions**: Given a `PrintJob` and a set of available `Printer` objects, the selected printer must be identical.
4. **State Transitions**: Given a `PrintJob` and a transition trigger, the resulting state must be identical.
5. **Policy Evaluation**: Given a policy and a set of inputs, the evaluation result must be identical.
6. **Event Ordering**: Given the same set of events, the emitted ordered stream must be identical.

## 3. Non-Deterministic Boundaries

The following components are explicitly non-deterministic and must be isolated behind interfaces:

1. **Provider Communication**: Network I/O with printers is inherently non-deterministic.
2. **Time**: `timestamp` values are non-deterministic and must be injected.
3. **Randomness**: Random number generation must use a seeded PRNG in deterministic mode.
4. **External State**: Reads from databases, caches, and external services are non-deterministic.
5. **Concurrency**: Thread scheduling is non-deterministic. Deterministic components must not depend on thread execution order.

## 4. Isolation Mechanism

- Deterministic components must be pure functions with no side effects.
- All non-deterministic inputs must be passed as explicit parameters.
- The system must provide a "deterministic mode" where all non-deterministic inputs are mocked or faked.

## 5. Time Injectability

- All timestamp generation must be abstracted behind a `Clock` interface.
- In deterministic mode, the `Clock` must return a fixed, incrementing timestamp.
- The system must never call `time.now()` or equivalent directly in deterministic components.

## 6. Randomness Injectability

- All random number generation must be abstracted behind a `Random` interface.
- In deterministic mode, the `Random` must use a fixed seed and produce a deterministic sequence.
- The system must never call `rand()` or equivalent directly in deterministic components.

## 7. Testing Requirements

- All deterministic components must have property-based tests.
- Tests must verify that identical inputs produce identical outputs across multiple runs.
- Tests must run in deterministic mode to eliminate flakiness.
- Fuzzing must be applied to deterministic components to find edge cases.

## 8. Simulation Alignment

- Simulations must run in deterministic mode.
- Simulation results must be reproducible: running the same simulation twice must produce identical results.
- Simulation seeds must be recorded and included in simulation reports.

## 9. Violations

- Any non-deterministic behavior in the deterministic core is a critical bug.
- The system must detect and log non-determinism in deterministic mode.
- Non-deterministic components must be thoroughly integration-tested but excluded from deterministic core tests.
