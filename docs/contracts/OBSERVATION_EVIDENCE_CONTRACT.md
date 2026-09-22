# Observation Evidence Contract

## Normative Status

This contract is normative.

## Scope

This contract defines how external observations are represented, stored, and interpreted within PrintForge.

## Observation vs Authority

An observation is evidence about physical state.

An observation is NOT authority over physical state.

The physical printer remains authoritative for physical state.

## Required Fields

Every PrinterObservation must retain:

* `timestamp` — when the observation was produced by the external source.
* `retrieval_timestamp` — when PrintForge retrieved the observation.
* `source` — the origin of the observation.
* `provider` — the provider that produced the observation.
* `provider_version` — the version of the provider.
* `raw_provider_data` — unmodified provider output.
* `normalized_data` — PrintForge-normalized representation.
* `epistemic_status` — the epistemic status of the observation.
* `provenance` — full provenance chain.

## Epistemic Status Values

* `DECLARED` — declared by provider without verification.
* `OBSERVED` — directly observed by provider.
* `DERIVED` — derived from other observations.
* `INFERRED` — inferred through reasoning.
* `ASSUMED` — assumed for control plane operation.
* `UNKNOWN` — unknown or not observed.
* `CONTRADICTED` — contradicted by subsequent evidence.
* `STALE` — older than the staleness threshold.

## Staleness

Staleness must be explicitly represented.

A stale observation must carry `epistemic_status = STALE`.

Stale observations must not be treated as current physical truth.

## Unknown Representation

Unknown information must be represented as `UNKNOWN`.

Unknown must not silently become `True` or `False`.

## Raw Provider Data

Raw provider data must be preserved.

Normalization must not discard provider-origin information.

## Reconciliation

When multiple observations conflict:

1. Retain all observations.
2. Mark the contradicted observation as `CONTRADICTED`.
3. Never silently overwrite prior observations.
