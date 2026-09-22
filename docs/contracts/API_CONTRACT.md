# API Contract

## 1. Versioning

- The API is versioned via the URL path: `/api/v1/...`.
- Breaking changes require a new API version.
- Non-breaking changes (new fields, new endpoints) may be added to the current version.
- Deprecated endpoints must return a `Sunset` header with the deprecation date.

## 2. Base URL

```
https://<host>/api/v1
```

## 3. Authentication

All requests must include an `Authorization` header:

```
Authorization: Bearer <token>
```

Or for mTLS:

```
Authorization: Bearer <client-cert-thumbprint>
```

## 4. Endpoints

### Jobs

#### Create Job

```
POST /jobs
```

Request:

```json
{
  "document_ref": { "document_id": "string" },
  "target_capabilities": [...],
  "priority": 0,
  "metadata": {},
  "retry_policy": { ... }
}
```

Response: `201 Created`

```json
{
  "job_id": "string",
  "state": "CREATED",
  "created_at": "timestamp",
  "links": { "self": "/api/v1/jobs/{job_id}" }
}
```

#### Get Job

```
GET /jobs/{job_id}
```

Response: `200 OK`

```json
{
  "job_id": "string",
  "state": "QUEUED",
  "created_at": "timestamp",
  ...
}
```

#### List Jobs

```
GET /jobs?state=QUEUED&limit=20&offset=0
```

Response: `200 OK`

```json
{
  "jobs": [...],
  "total": 100,
  "limit": 20,
  "offset": 0
}
```

#### Cancel Job

```
POST /jobs/{job_id}/cancel
```

Response: `202 Accepted`

```json
{
  "job_id": "string",
  "state": "CANCELLING"
}
```

### Printers

#### List Printers

```
GET /printers
```

Response: `200 OK`

```json
{
  "printers": [...]
}
```

#### Get Printer

```
GET /printers/{printer_id}
```

Response: `200 OK`

```json
{
  "printer_id": "string",
  "name": "string",
  "status": "IDLE",
  ...
}
```

#### Get Printer Observations

```
GET /printers/{printer_id}/observations?limit=20&offset=0
```

Response: `200 OK`

```json
{
  "observations": [...]
}
```

### Documents

#### Upload Document

```
POST /documents
Content-Type: application/octet-stream
```

Request: Raw bytes with `X-Document-Format` header.

Response: `201 Created`

```json
{
  "document_id": "string",
  "format": "PDF",
  "size_bytes": 1024,
  "hash": "sha256:..."
}
```

#### Get Document

```
GET /documents/{document_id}
```

Response: `200 OK` with raw bytes.

### Events

#### List Events

```
GET /events?aggregate_id={id}&limit=20&offset=0
```

Response: `200 OK`

```json
{
  "events": [...]
}
```

## 5. Error Responses

All errors follow this envelope:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {},
    "trace_id": "string",
    "timestamp": "timestamp"
  }
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 202 | Accepted (async operation) |
| 400 | Bad request (validation error) |
| 401 | Unauthenticated |
| 403 | Unauthorized |
| 404 | Not found |
| 409 | Conflict (idempotency violation) |
| 422 | Unprocessable entity (semantic error) |
| 429 | Rate limited |
| 500 | Internal server error |
| 503 | Service unavailable |

## 6. Pagination

- List endpoints support `limit` and `offset` query parameters.
- Default `limit`: 20. Maximum `limit`: 100.
- Responses include `total`, `limit`, and `offset` for client-side pagination.

## 7. Rate Limiting

- Requests are rate-limited per API key or user.
- Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1633046400
```

- Exceeding the rate limit returns HTTP 429.

## 8. Idempotency

- Mutating endpoints (`POST /jobs`, `POST /documents`) support an `Idempotency-Key` header.
- The system must return the same response for duplicate idempotency keys within 24 hours.
- Idempotency keys must be UUIDs or similar high-entropy strings.
