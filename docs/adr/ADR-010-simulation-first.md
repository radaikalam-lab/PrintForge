# ADR-010: Simulation-First Development

## Status

Accepted

## Context

PrintForge interacts with physical printers, which are expensive, scarce, and unreliable for development and testing. Developers need to:
- Write code without physical printers.
- Test edge cases (failures, timeouts, high load) that are hard to reproduce on real hardware.
- Run CI/CD without external dependencies.
- Demonstrate features without hardware.

We need a development and testing strategy that does not depend on physical printers.

## Decision

We adopt a simulation-first development approach:

1. **Simulator Provider**: A built-in provider that simulates printer behavior (see SIMULATOR_CONTRACT.md).
2. **Deterministic Mode**: The simulator runs in deterministic mode by default in tests.
3. **Test Scenarios**: Pre-defined test scenarios simulate common situations:
   - Happy path: job prints successfully.
   - Transient failure: printer fails once, then succeeds.
   - Permanent failure: printer is broken.
   - High load: many jobs queued simultaneously.
   - Network partition: provider becomes unreachable.
4. **Property-Based Testing**: The deterministic core is verified with property-based tests.
5. **CI/CD Integration**: All CI/CD pipelines use the simulator. Physical hardware tests are optional and run in a separate stage.

### Development Workflow

1. Developer writes feature against the simulator.
2. Developer runs unit tests with the simulator in deterministic mode.
3. Developer runs integration tests with the simulator in stochastic mode.
4. CI/CD runs the full test suite with the simulator.
5. Optional: hardware-in-the-loop tests run on dedicated hardware.

### Simulator Configuration

- Simulator behavior is configured via YAML or environment variables.
- Test scenarios are versioned and stored in the repository.
- Simulator logs are captured and attached to test reports.

### Hardware Testing

- Physical hardware tests are marked with a `hardware` tag.
- They run in a separate CI/CD stage with exclusive access to physical printers.
- They are optional and do not block merges.

## Consequences

### Positive

- Fast, reliable development without hardware.
- Comprehensive test coverage of edge cases.
- CI/CD is fast and deterministic.
- Features can be demonstrated without hardware.

### Negative

- Simulator fidelity: the simulator may not perfectly model real printer behavior.
- Hardware-specific bugs may only be caught in hardware tests.
- Maintaining the simulator requires effort.

### Neutral

- This approach is common in hardware-adjacent software (e.g., embedded systems, IoT).
- Simulator fidelity improves over time as we discover discrepancies with real hardware.

## References

- SIMULATOR_CONTRACT.md
- DETERMINISM_CONTRACT.md
- PRINTFORGE_SYSTEM_CONTRACT.md (Design Philosophy)
