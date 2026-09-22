# Epistemic Boundary Contract

## Normative Status

This contract is normative. Implementation must conform to this contract.

## Boundary Definition

The epistemic layer exists as an advisory/qualifying layer above the application/control plane.

The epistemic layer:

1. Cannot directly execute printer operations.
2. Cannot directly mutate PrintJob execution state.
3. Cannot bypass domain validation.
4. Cannot bypass policy.
5. Cannot invoke physical-device providers.
6. Cannot represent advisory information as physical authority.

## Advisory Relationship

```text
Epistemic Layer
        │
        │ advisory / qualifying
        ▼
Application / Control Plane
        │
        │ validated execution
        ▼
Provider
        │
        ▼
Physical Device
```

## Prohibited Actions

Epistemic components must not:

* Call provider methods that perform device operations.
* Modify domain state without passing through application services.
* Emit domain events that imply physical truth.
* Bypass state machine validation.
* Override policy decisions.

## Required Actions

Epistemic components must:

* Retain provenance for all observations.
* Distinguish observed facts from inferred facts.
* Mark stale observations explicitly.
* Represent unknown information as UNKNOWN.
* Never silently convert unknown to true or false.

## Integration Point

Epistemic components may:

* Subscribe to domain events.
* Query read-only repositories.
* Emit advisory events with epistemic status.
* Provide qualifying metadata for scheduling and policy.

Epistemic components must never:

* Write to execution state.
* Submit jobs to providers.
* Cancel jobs directly.
* Control devices.
