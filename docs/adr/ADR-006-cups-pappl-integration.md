# ADR-006: CUPS and PAPPL Integration

## Status

Accepted

## Context

PrintForge runs on Linux containers. The dominant printing system on Linux is CUPS (Common UNIX Printing System). CUPS provides:
- A spooler and scheduler.
- IPP backend support.
- Printer discovery and configuration.
- Driver management.

PAPPL (Printer Application) is a newer framework for building printer applications. PAPPL provides:
- A modern, modular architecture.
- Built-in IPP support.
- Driver abstraction.
- Multi-architecture support.

We need to decide how PrintForge integrates with CUPS and PAPPL.

## Decision

We will integrate with both CUPS and PAPPL, treating them as provider types:

1. **CUPS Provider**: A provider that uses the CUPS API (via `libcups` or IPP-over-HTTP) to manage CUPS queues and send jobs.
2. **PAPPL Provider**: A provider that uses the PAPPL API to manage printer applications.
3. **Provider Isolation**: Both CUPS and PAPPL providers implement the same `Provider` interface. The PrintForge core is unaware of which provider type is in use.
4. **Deployment Flexibility**: Users may choose CUPS, PAPPL, or both, depending on their environment.

### CUPS Provider Details

- Uses `libcups` for queue management and IPP for job submission.
- Maps CUPS queues to PrintForge printers.
- Translates PrintForge capabilities to CUPS IPP attributes.
- Observes CUPS queue state for printer observations.

### PAPPL Provider Details

- Uses PAPPL's driver model for capability discovery.
- Maps PAPPL printer objects to PrintForge printers.
- Uses PAPPL's IPP implementation for job submission.
- Observes PAPPL printer state for observations.

## Consequences

### Positive

- We leverage mature, well-tested printing infrastructure.
- CUPS and PAPPL handle driver management, device discovery, and low-level protocol details.
- Users can migrate from CUPS to PAPPL without changing PrintForge configuration (much).
- Both CUPS and PAPPL support IPP natively, simplifying provider implementation.

### Negative

- CUPS and PAPPL are Linux-specific. We cannot deploy on Windows without additional providers.
- CUPS configuration is complex and varies across distributions.
- PAPPL is newer and less widely deployed than CUPS.

### Deployment Boundary

CUPS and PAPPL adapters run in a separate integration/runtime boundary from the PrintForge core. The core itself maintains the non-root container principle. CUPS/PAPPL providers may require elevated privileges or device access; the final deployment mechanism is deferred to a future operational ADR. The general non-root principle is not weakened for the core.

### Neutral

- CUPS and PAPPL providers share significant code (IPP translation, observation mapping).
- We may need to provide Docker images with CUPS or PAPPL pre-configured.

## References

- CUPS Documentation: https://www.cups.org/doc/
- PAPPL Documentation: https://www.pappl.app/
