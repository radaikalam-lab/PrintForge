# ADR-005: Docker and Linux Deployment

## Status

Accepted

## Context

PrintForge must be deployed in production environments. Key requirements:
- Consistency across development, testing, and production.
- Isolation from host system dependencies.
- Easy scaling and orchestration.
- Support for CI/CD pipelines.

Linux containers (Docker or compatible) are the industry standard for meeting these requirements.

## Decision

We require Docker and Linux for all production deployments:

1. **Container Images**: PrintForge is distributed as Docker images.
2. **Linux Base**: All images are based on Linux (Alpine or Debian).
3. **Single Binary**: The application is compiled to a single static binary (e.g., via Go or Rust).
4. **Docker Compose**: Development and testing use Docker Compose.
5. **Kubernetes**: Production orchestration uses Kubernetes.
6. **No Root**: Containers run as non-root users.
7. **Minimal Images**: Images are minimal, containing only the binary and necessary certificates.

### Container Architecture

```
+------------------+
|   Ingress        |
+--------+---------+
         |
+--------v---------+
|   PrintForge API |
|   (single binary)|
+--------+---------+
         |
+--------v---------+
|   Spool Backend  |
|   (S3 or DB)     |
+--------+---------+
         |
+--------v---------+
|   Provider 1     |
|   (CUPS)         |
+--------+---------+
+--------v---------+
|   Provider 2     |
|   (PAPPL)        |
+--------+---------+
```

### Security

- Containers run as non-root.
- Read-only root filesystem where possible.
- Secrets injected via environment or mounted files.
- No privileged mode.

### Observability

- Structured logs to stdout/stderr.
- Metrics exposed via Prometheus endpoint.
- Traces exported via OpenTelemetry.

## Consequences

### Positive

- Consistent environments from development to production.
- Easy deployment and scaling.
- Strong isolation between components.
- Wide ecosystem support (Docker, Kubernetes, CI/CD).

### Negative

- Windows and macOS are not supported for production.
- Container orchestration adds operational complexity.
- Debugging containerized applications may be harder.

### Neutral

- Linux containers are the industry standard. Most printing infrastructure already runs on Linux.
- Docker Desktop on macOS/Windows is supported for development only.

## References

- PRINTFORGE_SYSTEM_CONTRACT.md (Deployment Constraints)
- Docker Documentation: https://docs.docker.com/
- Kubernetes Documentation: https://kubernetes.io/docs/
