# Architecture

PrintForge follows a layered, local-first architecture with strict boundaries between the API surface, domain logic, and hardware adapters.

## Layers

```
┌─────────────────────────────────────────────┐
│              HTTP / API Layer               │
│         FastAPI + Pydantic Models           │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│           Application / Service Layer        │
│      Use cases, orchestration, validation    │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│           Domain / Contract Layer            │
│   Interfaces, repositories, provider contracts│
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│              Provider Layer                  │
│  Protocol adapters: IPP, LPD, AppSocket, etc │
└─────────────────────────────────────────────┘
```

## Contracts

All inter-layer communication goes through explicit contracts:

- **Repository interfaces** abstract data access (SQLite, in-memory, etc.).
- **Provider interfaces** abstract printer and job operations.
- **Event interfaces** abstract event streaming (SSE, WebSocket, polling).

The API layer never directly instantiates a hardware provider; dependencies are injected.

## Provider Boundaries

Providers must not leak protocol details to upper layers. They translate native printer responses into domain models and raise standardized exceptions. This keeps the API stable even when underlying protocols change.

## Data Storage

- **Local-first**: default storage is a local SQLite database.
- **Event sourcing**: job events are append-only for auditability.
- **No mandatory cloud sync**: all state is local unless explicitly mirrored.

## Deployment Topology

- **Single-node**: typical deployment is one PrintForge instance per host or container.
- **CUPS integration**: PrintForge can act as a control plane in front of CUPS or PAPPL, or replace it for appliance-style setups.
- **Simulator mode**: all hardware providers can be swapped for a simulator, enabling zero-hardware testing and CI.
