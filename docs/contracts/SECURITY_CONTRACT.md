# Security Contract

## 1. Security Boundary

PrintForge's security boundary encompasses all components within the system boundary defined in PRINTFORGE_SYSTEM_CONTRACT.md. The boundary includes:

- API endpoints
- Provider interfaces
- Spool storage
- Event bus
- Internal services

The boundary explicitly excludes:
- Physical printer hardware
- Client applications
- External identity providers

## 2. Authentication

### API Authentication

- All API requests must be authenticated.
- Supported authentication methods:
  - Bearer token (JWT or opaque)
  - mTLS client certificates
  - API key (for service-to-service)
- Authentication failures must return HTTP 401.
- Authentication must be stateless where possible.

### Provider Authentication

- Providers must authenticate to the PrintForge control plane.
- Provider authentication must use mTLS or mutual bearer tokens.
- Provider credentials must be rotated every 90 days.
- Provider authentication failures must result in connection refusal.

## 3. Authorization

### Role-Based Access Control (RBAC)

```yaml
Role:
  name: string (immutable)
  permissions: Permission[]

Permission:
  resource: string (e.g., "job", "printer", "document")
  actions: string[] (e.g., ["create", "read", "update", "delete"])
  conditions: Condition[] (optional)

Condition:
  field: string
  operator: string (e.g., "eq", "in")
  value: any
```

### Roles

| Role | Description |
|------|-------------|
| admin | Full access to all resources. |
| operator | Create jobs, read printers, read documents. |
| viewer | Read-only access to jobs and printers. |
| provider | Manage own printers and execute jobs. |

### Authorization Rules

1. Authorization must be checked on every API request.
2. Authorization must be checked on every provider operation.
3. Authorization checks must be logged.
4. Authorization failures must return HTTP 403.
5. Authorization must be enforced at the API gateway and validated again at the service level.

## 4. Data Protection

### Encryption in Transit

- All network communication must use TLS 1.3 or higher.
- TLS must be configured with secure cipher suites.
- Certificate validation must not be disabled in production.

### Encryption at Rest

- All spool documents must be encrypted at rest (see SPOOL_CONTRACT.md).
- All database records must be encrypted at rest.
- Encryption keys must be managed by a KMS or HSM.
- Keys must be rotated annually.

### Secrets Management

- Secrets must never be hardcoded.
- Secrets must be injected via environment variables, secret mounts, or secret management APIs.
- Secrets must not be logged.
- Secrets must not appear in error messages.

## 5. Input Validation

- All API inputs must be validated against schemas.
- All provider inputs must be validated against schemas.
- Invalid inputs must be rejected with HTTP 400.
- Validation must prevent injection attacks (SQL, NoSQL, command injection, XSS).
- File uploads must be scanned for malware.
- File uploads must be size-limited (see DOCUMENT_CONTRACT.md).

## 6. Audit Logging

- All authentication events must be logged.
- All authorization decisions must be logged.
- All state transitions must be logged.
- All document access must be logged.
- All provider actions must be logged.
- Logs must be tamper-evident.
- Logs must be retained for 7 years.

### Audit Log Entry

```yaml
AuditLogEntry:
  timestamp: timestamp
  actor: string (user_id, provider_id, or "system")
  action: string
  resource_type: string
  resource_id: string
  result: "success" | "failure"
  reason: string | null
  ip_address: string | null
  user_agent: string | null
  trace_id: string
```

## 7. Threat Mitigation

| Threat | Mitigation |
|--------|------------|
| Unauthorized job submission | Authentication + authorization + input validation |
| Job tampering | Immutable job definition + hash verification |
| Document exfiltration | Encryption at rest + access control + audit logging |
| Provider impersonation | mTLS + certificate pinning |
| Replay attacks | Nonce + timestamp validation |
| Denial of service | Rate limiting + circuit breakers + resource quotas |
| Data corruption | Checksums + replication + backup |
| Privilege escalation | RBAC + principle of least privilege |

## 8. Security Testing

- All authentication and authorization paths must be covered by security tests.
- Penetration testing must be performed before each major release.
- Dependency scanning must be part of CI/CD.
- Secrets must not be detectable in code or logs via automated scanning.
