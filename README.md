# PrintForge

**Open, Local-First Printing Control Plane**

PrintForge is an open-source, local-first control plane for managing printers, print jobs, and device capabilities. It provides a versioned REST API, hardware-agnostic abstractions, and a simulator for testing without physical printers.

## What PrintForge is

- A **versioned FastAPI control plane** for printer discovery, job management, and status monitoring.
- A **local-first architecture** that runs on a single host (or container) with file-based storage by default.
- A **hardware-agnostic abstraction layer** with provider-based integration for real printer protocols.
- A **simulator** for development and CI testing without physical hardware.

## What PrintForge is not

- A CUPS replacement or print spooler front-end (though it can integrate with one).
- A cloud-only SaaS requiring external connectivity.
- A desktop GUI application.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for a detailed breakdown of layers, contracts, and provider boundaries.

## Supported Protocols

PrintForge abstracts printer communication through provider interfaces. Supported or planned protocols include:

- **PAPPL** (Printer Application Framework)
- **IPP / IPPS** (Internet Printing Protocol)
- **AppSocket** (port 9100 raw TCP)
- **LPD** (Line Printer Daemon)
- **USB** (via backend abstraction)

Protocol-specific providers implement a common `PrinterProvider` interface, allowing the API to remain decoupled from hardware.

## Deployment

### Docker Compose (development)

```bash
docker compose -f docker/compose.yaml up --build
```

The API is available at `http://localhost:8000`. OpenAPI docs at `http://localhost:8000/docs`.

### Production

For production, run behind a reverse proxy (nginx, Caddy) with TLS termination. Use a process manager (systemd, Supervisor) or orchestrate with Docker/Kubernetes.

## Simulator

PrintForge includes an in-memory simulator for API testing and development. The simulator returns mock printer data, job state transitions, and event streams without requiring hardware.

Enable the simulator by using the `SimulatorProvider` and `SimulatorRepository` dependencies. CI uses the simulator by default.

## Hardware Integration

Hardware integration happens through **providers**. Each provider implements the abstract interfaces defined in `server/providers/`. Providers encapsulate protocol details, connection management, and state mapping.

To integrate a new printer or protocol:

1. Implement `PrinterProvider` for discovery, capabilities, and status.
2. Implement `JobProvider` for job submission, cancellation, and events.
3. Register the provider in the dependency injection container.

## Contract Philosophy

PrintForge treats API contracts as first-class artifacts:

- **Stable `/api/v1` routes** with explicit Pydantic request/response models.
- **Versioned responses** so breaking changes require a new API version (`/api/v2`, etc.).
- **Contract tests** in `tests/` that validate request/response schemas.
- **Provider contracts** that enforce boundaries between the API layer and hardware adapters.

Breaking a contract requires a deliberate version bump and migration guide.

## Development Workflow

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, testing, and release guidelines.
