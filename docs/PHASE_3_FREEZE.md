# Phase 3 Freeze

## 1. Phase 3 Scope

Phase 3 covers API integration and the epistemic boundary. It establishes the authoritative application authority model, the single-writer state ownership rule, provider isolation, and the advisory epistemic layer.

## 2. Implemented Capabilities

- FastAPI v1 API with dependency injection
- Application service layer (PrintJobService, PrinterService)
- Deterministic error hierarchy and HTTP mapping
- Epistemic boundary enforcement
- Stale observation age semantics with FreshnessPolicy
- Declared vs observed capability reconciliation
- Full provenance retention
- Simulation-first testing with DeterministicPrinterSimulator
- In-memory persistence for development and testing

## 3. Normative Contracts

- PRINTFORGE_SYSTEM_CONTRACT.md
- API_CONTRACT.md
- PRINT_JOB_CONTRACT.md
- PRINTER_CONTRACT.md
- EXECUTION_CONTRACT.md
- CAPABILITY_CONTRACT.md
- OBSERVATION_CONTRACT.md
- OBSERVATION_EVIDENCE_CONTRACT.md
- EPISTEMIC_BOUNDARY_CONTRACT.md
- EPISTEMIC_PROVENANCE_CONTRACT.md
- EVENT_CONTRACT.md
- FAILURE_CONTRACT.md
- DETERMINISM_CONTRACT.md
- SECURITY_CONTRACT.md
- SIMULATOR_CONTRACT.md
- SPOOL_CONTRACT.md
- DOCUMENT_CONTRACT.md
- PROVENANCE_CONTRACT.md
- PROVIDER_CONTRACT.md

## 4. Epistemic Boundary

The epistemic subsystem is an advisory/qualifying overlay. It qualifies observations with freshness, staleness, aging, and consistency status. It informs control-plane decisions but never executes printer operations or bypasses validation. Only explicit application services and authorized provider interfaces may mutate domain state.

Key rules:
- Epistemic records cannot mutate production state.
- Epistemic records cannot authorize execution.
- Stale observations cannot silently become fresh.
- Contradictions must remain visible.
- Unknown must not silently become false.

## 5. Known Limitations

- SQLite persistence is synchronous and not production-grade.
- No IPP, CUPS, or PAPPL provider implementations yet.
- No S3/Kafka/KMS integration in local development baseline.
- No web frontend or UI.
- Confidence is not numerically defined.
- No cryptographic provenance signing (KMS deferred).

## 6. Deferred Work

- IPP implementation
- CUPS/PAPPL integration
- OpenPrinter integration
- Physical hardware testing
- Advanced epistemic reasoning
- AI integration
- Production-grade persistence (PostgreSQL)
- Event streaming (Kafka)
- Object storage (S3)
- KMS integration
- Cryptographic provenance signing

## 7. Test Baseline

- 56 passed
- 2 skipped (hardware/container)
- 0 failed
- Lint: PASS (ruff)
- Typecheck: PASS (mypy)
- Docker: environment-limited (local install succeeds)

## 8. Next Phase

**Phase 4 — Spool and Document Pipeline**

Phase 4 will address:
- spool artifact model
- document lifecycle
- artifact integrity
- source document
- normalized document
- rendered/device-ready representation
- storage abstraction
- lifecycle/cleanup
- duplicate detection
- crash recovery
- provenance

Do NOT implement IPP/CUPS in Phase 4.
