# ADR-021: Physical Hardware Boundary

## Status

Accepted

## Context

PrintForge orchestrates print jobs but does not manufacture or directly control printers. The physical world introduces constraints and failure modes that software alone cannot resolve.

We need a clear boundary between the software system and physical hardware to:
- Prevent the system from making unsafe assumptions about hardware state.
- Ensure that hardware failures are handled gracefully.
- Define clear responsibilities between software and hardware.

## Decision

We establish a strict physical hardware boundary:

1. **Provider-Mediated Command**: The system commands hardware only through providers, under contract. It never manipulates hardware directly.
2. **Provider-Mediated Observation**: The system observes hardware state via providers but never treats provider reports as authoritative physical truth.
3. **Provider Role**: Providers are both command interfaces and observation interfaces. Providers may command printer operations under contract. Providers may observe printer state. Providers do not own physical truth. Providers do not mutate PrintForge domain state.
4. **Printer Authority**: The physical printer remains authoritative for physical reality.
5. **Graceful Degradation**: Hardware failures are treated as provider failures. The system continues operating with remaining hardware.
6. **Physical Assumptions Documented**: Any physical assumptions (e.g., "paper is loaded," "toner is present") are documented as provider-reported observations, not software facts.

### Distinction

```text
Provider
    = command interface + observation interface

Printer
    = physical authority
```

Therefore:

```text
Provider may command
Provider may observe
Provider does not own physical truth
Provider does not mutate PrintForge domain state
```

### Boundary Rules

| Software Action | Hardware Action |
|-----------------|-----------------|
| Send print request via Provider | Provider translates to printer language |
| Query printer status via Provider | Provider reads hardware sensors |
| Cancel job via Provider | Provider sends cancel command to printer |
| Observe metrics via Provider | Provider reads hardware telemetry |

### Hardware Failure Handling

- If a provider reports a hardware failure, the printer is marked ERROR or OFFLINE.
- The system does not retry jobs on failed hardware unless the failure is transient (e.g., paper jam cleared).
- The system may alert operators to physical interventions required (e.g., "replace toner").

### Safety

- The system must not send commands that could damage hardware (e.g., invalid firmware updates).
- Providers must validate commands against printer capabilities before sending.
- The system must have a kill switch to stop all outgoing commands in an emergency.

## Consequences

### Positive

- Clear separation of concerns between software and hardware.
- Hardware failures are isolated and do not crash the software.
- The system is safe: it cannot cause physical damage because it never touches hardware directly.
- Provider reports are correctly treated as observations, not authoritative physical truth.

### Negative

- The system relies on providers to correctly interpret hardware state. Buggy providers may misreport state.
- Some hardware features may not be exposed via standard protocols, limiting functionality.

### Neutral

- This boundary is similar to other orchestration systems (e.g., Kubernetes does not directly control servers).
- Providers must be carefully designed and tested for hardware interaction.

## References

- PRINTFORGE_SYSTEM_CONTRACT.md (Architectural Laws)
- OBSERVATION_CONTRACT.md (Observation vs. Authority)
- PROVIDER_CONTRACT.md (Provider Interface)
