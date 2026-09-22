# Capability Contract

## 1. PrinterCapabilities Object

`PrinterCapabilities` defines the declarative, machine-readable capabilities of a printer.

```yaml
PrinterCapabilities:
  version: string (semver, immutable)
  color: boolean
  duplex: boolean
  max_width_mm: integer (>0)
  max_height_mm: integer (>0)
  min_width_mm: integer (>0)
  min_height_mm: integer (>0)
  supported_media: MediaCapability[]
  supported_qualities: QualityCapability[]
  supported_sources: SourceCapability[]
  max_copies: integer (>0)
  resolution_dpi: ResolutionCapability
  custom: map<string, any>
```

## 2. MediaCapability

```yaml
MediaCapability:
  media_type: string (e.g., "plain", "photo", "envelope", "label")
  weight_gsm: [min: integer, max: integer]
  size: MediaSize (ISO or custom)
```

## 3. QualityCapability

```yaml
QualityCapability:
  quality: string (e.g., "draft", "normal", "high")
  resolution_dpi: [horizontal: integer, vertical: integer]
```

## 4. SourceCapability

```yaml
SourceCapability:
  source_id: string
  type: string (e.g., "tray1", "manual", "bypass")
  capacity: integer | null
  media_types: string[]
```

## 5. ResolutionCapability

```yaml
ResolutionCapability:
  horizontal: integer
  vertical: integer
```

## 6. Capability Requirement Matching

A `CapabilityRequirement` (from a PrintJob) matches a `PrinterCapabilities` if and only if:

1. **Color**: If `color` is `true`, the printer must have `color: true`.
2. **Duplex**: If `duplex` is `true`, the printer must have `duplex: true`.
3. **Dimensions**: The job's media size must fit within the printer's `[min_width_mm, max_width_mm]` and `[min_height_mm, max_height_mm]`.
4. **Media**: The job's required `media_type` must be present in `supported_media`.
5. **Quality**: The job's required `quality` must be present in `supported_qualities`.
6. **Copies**: The job's `copies` must be <= `max_copies`.
7. **Resolution**: The job's required resolution must be <= the printer's resolution.
8. **Custom**: Any custom requirements must match exactly or within declared bounds.

## 7. Versioning

- `PrinterCapabilities.version` uses semantic versioning.
- Capability schemas are versioned. A printer's capabilities version must be compatible with the system's capability schema version.
- Incompatible capability versions must cause registration failure.

## 8. Immutability

- Once registered, a `PrinterCapabilities` object is immutable.
- If a printer's capabilities change, the printer must be re-registered with a new `printer_id`.
- The system must retain historical capability records for audit and provenance.

## 9. Declarative Semantics

- Capabilities are declarative assertions by the provider.
- The system may verify capabilities at registration time but must trust them during routing unless contradicted by observation.
- Contradiction between declared capabilities and observation must trigger a `CapabilityMismatch` event and mark the printer `DEGRADED`.

## 10. Capability Reconciliation

- Declared capabilities and observed capabilities must be reconciled explicitly.
- Reconciliation outcome values: `ACCEPTED`, `ACCEPTED_WITH_STALE_EVIDENCE`, `CONFLICT`, `UNRESOLVED`, `UNAVAILABLE`.
- `ACCEPTED` — observed capabilities match declared capabilities and evidence is fresh.
- `ACCEPTED_WITH_STALE_EVIDENCE` — observed capabilities match declared capabilities but evidence is stale.
- `CONFLICT` — observed capabilities differ from declared capabilities.
- `UNRESOLVED` — evidence is insufficient or unavailable.
- `UNAVAILABLE` — observation is unavailable; declared capabilities remain the only source of truth.
- Reconciliation must preserve both declared and observed capability sets with full provenance.
- Capability values are distinct from observation/query execution results. A failed capability query is represented as `UNAVAILABLE`, not as a capability value.
