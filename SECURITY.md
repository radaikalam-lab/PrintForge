# Security Policy

## Security Boundary

PrintForge is designed to run on a **local, trusted network**. It is not hardened for direct exposure to the public internet.

### Trusted Zone

- The API should be deployed behind a firewall or within a trusted LAN.
- When exposed externally, it must be protected by a reverse proxy with authentication and TLS termination.
- Default SQLite storage is file-system protected; ensure the host OS permissions restrict access.

### API Authentication

- Current API version (`/api/v1`) does not enforce authentication.
- Future versions may add token-based auth (API keys, OAuth2). Do not rely on the absence of auth as a security control.

### Provider Isolation

- Hardware providers run in-process. A compromised provider could access the host system.
- Containerized deployments should run PrintForge as a non-root user.
- Future architecture may support out-of-process providers with capability restrictions.

### Data Privacy

- PrintForge does not send data to external services by default.
- Job metadata, document content, and device states remain local unless explicitly exported.

## Reporting Vulnerabilities

Report security issues privately via the project's security contact or GitHub Security Advisories. Do not open public issues for active vulnerabilities.
