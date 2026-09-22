# Epistemic Provenance Contract

## Normative Status

This contract is normative.

## Principle

Every normalized fact derived from an external provider must retain provenance.

## Required Provenance Fields

For observations:

* `source` — the observation source.
* `provider` — the provider identifier.
* `provider_version` — the provider version.
* `timestamp` — the observation timestamp.
* `retrieval_timestamp` — when PrintForge retrieved the observation.
* `raw_reference` — reference to raw provider data.
* `normalization_version` — the version of normalization logic applied.

For domain events:

* `source` — what triggered the event.
* `provider` — the provider involved, if any.
* `provider_version` — the provider version.
* `timestamp` — when the event occurred.

## Non-Discard

Provenance must never be discarded because data has been normalized.

Normalized data and provenance must remain separable.

## Traceability

Given a domain event or observation, it must be possible to trace back to:

1. The raw provider response.
2. The provider identity and version.
3. The normalization logic version.
4. The timestamp of retrieval.

## Auditability

The audit log must contain:

* What PrintForge believed.
* What PrintForge requested.
* What the printer reported.

Belief and report must remain distinguishable.
