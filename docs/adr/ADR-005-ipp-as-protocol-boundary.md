# ADR-005: IPP as Protocol Boundary

## Status

Accepted

## Context

PrintForge must integrate with a wide variety of printers and printing systems. Printers speak different protocols: IPP (Internet Printing Protocol), CUPS (Common UNIX Printing System), PAPPL (Printer Application), and proprietary vendor protocols.

We need a clear boundary between the PrintForge core and the diverse printing protocols. Without a clear boundary, protocol-specific logic will leak into the core, making it brittle and hard to test.

## Decision

We define IPP as the canonical protocol boundary used across the Provider interface. All provider implementations must translate printer-specific protocols to/from IPP semantics before interacting with the PrintForge core.

Specifically:

1. **IPP as Lingua Franca**: IPP 2.0+ is the canonical internal representation used across the provider boundary for standard printer operations.
2. **Provider Translation**: Providers translate between printer-native protocols and IPP. Non-IPP devices are handled by provider-specific bridges or adapters.
3. **Core Agnosticism**: The PrintForge core communicates with printer integrations only through the Provider interface. It does not speak IPP directly, nor does it depend on IPP libraries in the domain layer.
4. **Capability Mapping**: Printer capabilities are mapped to IPP attributes (e.g., `printer-resolution`, `sides`).

## Consequences

### Positive

- The core is protocol-agnostic. Adding support for a new printer protocol only requires a new provider.
- IPP is a well-documented, widely-supported standard.
- IPP's attribute model maps naturally to our capability system.
- Testing is simplified: we can test against an IPP simulator instead of real hardware.

### Negative

- Protocol translation adds complexity to provider implementations.
- IPP may not expose all printer-specific features. We lose access to vendor extensions.
- IPP implementations vary. We must handle IPP dialect differences.

### Neutral

- CUPS and PAPPL both support IPP natively, so translation is straightforward for Linux deployments.
- For legacy printers without IPP, we need protocol bridges or custom providers.

## References

- RFC 8011: Internet Printing Protocol
- CUPS IPP Support: https://www.cups.org/doc/ipp.html
- PAPPL IPP Support: https://www.pappl.app/
