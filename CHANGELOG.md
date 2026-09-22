# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-22

### Added
- Versioned FastAPI application under `/api/v1`.
- Printer endpoints: list, detail, capabilities, status.
- Job endpoints: create, list, detail, cancel, events.
- Dependency-injected repositories and providers for printers, jobs, and events.
- Docker multi-stage development image.
- Docker Compose with `printforge` service and commented CUPS stub.
- GitHub Actions CI workflow running pytest on `ubuntu-latest` with Python 3.12.
- Documentation: README, ARCHITECTURE, CONTRIBUTING, SECURITY, CHANGELOG.
- Project metadata via `pyproject.toml` (Hatchling build backend).
- Test suite using `pytest` and FastAPI `TestClient`.
