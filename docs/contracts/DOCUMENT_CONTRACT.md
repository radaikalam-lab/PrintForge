# Document Contract

## 1. DocumentReference Object

A `DocumentReference` is an immutable pointer to a document stored in the spool.

```yaml
DocumentReference:
  document_id: string (UUID v7, immutable)
  format: DocumentFormat (immutable)
  size_bytes: integer (>0, immutable)
  hash: string (SHA-256, immutable)
  created_at: timestamp (immutable)
  spool_path: string (immutable, backend-dependent)
```

### Fields

- **document_id**: Unique document identifier.
- **format**: The document format (see Format Enum).
- **size_bytes**: Size in bytes.
- **hash**: SHA-256 hash of the document content. Must be verified on ingest and retrieval.
- **created_at**: Timestamp of creation.
- **spool_path**: Backend-specific path or key.

## 2. DocumentFormat Enum

| Value | Description |
|-------|-------------|
| PDF | Portable Document Format. |
| POSTSCRIPT | PostScript document. |
| PCL | Printer Command Language. |
| PNG | Raster image. |
| JPEG | Raster image. |
| TIFF | Raster image. |
| TEXT | Plain text. |
| RAW | Raw printer data. |

## 3. Document Representation

Documents are represented as byte streams. The system must not interpret document content beyond:
- Format detection (via magic bytes or extension).
- Hash computation.
- Size validation (max 500MB).

## 4. Ingest Process

1. Client uploads document bytes.
2. System computes `hash` and `size_bytes`.
3. System validates format against declared format.
4. System stores document in spool via atomic write.
5. System returns `DocumentReference`.

### Ingest Rules

- Ingest must fail if `hash` does not match computed hash.
- Ingest must fail if `size_bytes` exceeds `max_document_size` (configurable, default 500MB).
- Ingest must fail if format is unsupported.
- Ingest must be idempotent: duplicate `document_id` with same content returns existing reference.

## 5. Retrieval Process

1. Client requests document by `document_id`.
2. System retrieves document from spool.
3. System verifies `hash` matches stored hash.
4. System returns document bytes.

### Retrieval Rules

- Retrieval must fail if document is not found.
- Retrieval must fail if hash verification fails (indicates corruption).
- Retrieval must emit `DocumentRetrieved` event.

## 6. Mutability

- Documents are immutable once stored.
- To "update" a document, a new `document_id` must be created.
- The old document may be retained per retention policy.

## 7. Streaming

- Documents must be streamed, not loaded entirely into memory, for documents > 10MB.
- The streaming interface must support range requests for partial retrieval.

## 8. Security

- Documents must be scanned for malware at ingest (see SECURITY_CONTRACT.md).
- Document access must be logged (see AUDIT requirements in SECURITY_CONTRACT.md).
- Documents must be encrypted in transit (TLS) and at rest (spool encryption).
