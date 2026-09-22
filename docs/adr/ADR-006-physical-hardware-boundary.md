# ADR-006: Physical Hardware Boundary

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

1. **No Direct Control**: PrintForge never sends electrical signals, opens hardware gates, or manipulates physical mechanisms.
2. **Provider Mediation**: All hardware interaction is mediated by providers. Providers translate software commands to hardware-specific protocols.
3. **Observable, Not Controllable**: The system observes hardware state via providers but does not directly control hardware.
4. **Graceful Degradation**: Hardware failures are treated as provider failures. The system continues operating with remaining hardware.
5. **Physical Assumptions Documented**: Any physical assumptions (e.g., "paper is loaded," "toner is present") are documented as provider-reported observations, not software facts.

### Boundary Rules

| Software Action | Hardware Action |
|-----------------|-----------------|
| Send IPP Print-Job request | Provider translates to printer language |
| Query printer status | Provider reads hardware sensors |
| Cancel job | Provider sends cancel command to printer |
| Observe metrics | Provider reads hardware telemetry |

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
