# ADR-018: Document Representation

## Status

Accepted

## Context

PrintForge handles documents of various formats: PDF, PostScript, PCL, images, and raw printer data. Documents may be large (hundreds of megabytes) and must be stored, transmitted, and processed efficiently.

We need a document representation that:
- Is format-agnostic at the core.
- Supports efficient storage and retrieval.
- Enables validation and integrity checking.
- Is secure (no code execution, no malware).

## Decision

We adopt a canonical, format-agnostic document representation:

1. **DocumentReference**: A document is represented by an immutable `DocumentReference` containing `document_id`, `format`, `size_bytes`, and `hash`.
2. **Byte Stream**: The actual document content is an opaque byte stream stored in the spool.
3. **Format Detection**: Format is detected at ingest via magic bytes or declared by the client.
4. **Hash Verification**: SHA-256 hash is computed at ingest and verified on every retrieval.
5. **Size Limits**: Documents are limited to 500MB by default (configurable).
6. **No Interpretation**: The core never interprets document content. Interpretation is delegated to providers.

### Document Storage

- Documents are stored in the spool as byte streams.
- Storage is atomic: a document is either fully written or not written at all.
- Documents are immutable once stored.
- Documents are addressable by `document_id`.

### Document Retrieval

- Documents are retrieved by `document_id`.
- Retrieval verifies the hash before returning bytes.
- Documents are streamed, not loaded entirely into memory, for large files.

### Format Handling

- The core validates format at ingest but does not convert between formats.
- Providers may convert formats if needed (e.g., PDF to PCL).
- Format conversion is a provider responsibility, not a core responsibility.

### Security

- Documents are scanned for malware at ingest.
- Document access is logged and audited.
- Documents are encrypted in transit and at rest.

## Consequences

### Positive

- The core is format-agnostic and simple.
- Large documents are handled efficiently via streaming.
- Integrity is guaranteed by hash verification.
- Security is enforced at the boundary.

### Negative

- No built-in format conversion. Users must ensure their documents are in a supported format.
- Large documents may stress the spool and network.

### Neutral

- This approach is similar to object storage systems (S3, GCS).
- Future format support is added by updating the ingest validator and provider translation, not the core.

## References

- DOCUMENT_CONTRACT.md
- SPOOL_CONTRACT.md
- SECURITY_CONTRACT.md
