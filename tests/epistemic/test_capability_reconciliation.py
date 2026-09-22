from datetime import datetime

from domain.capabilities import (
    CapabilityReconciliationStatus,
    reconcile_capabilities,
)


def test_declared_supported_observed_supported():
    declared = {"color": True, "duplex": False}
    observed = {"color": True, "duplex": False}
    rec = reconcile_capabilities(
        "printer-1",
        declared,
        observed,
        status=CapabilityReconciliationStatus.ACCEPTED,
    )
    assert rec.status == CapabilityReconciliationStatus.ACCEPTED
    assert rec.declared_capabilities == declared
    assert rec.observed_capabilities == observed


def test_declared_supported_observed_unsupported():
    declared = {"color": True, "duplex": False}
    observed = {"color": True, "duplex": True}
    rec = reconcile_capabilities(
        "printer-1",
        declared,
        observed,
        status=CapabilityReconciliationStatus.CONFLICT,
    )
    assert rec.status == CapabilityReconciliationStatus.CONFLICT
    assert rec.declared_capabilities == declared
    assert rec.observed_capabilities == observed


def test_declared_supported_observation_unavailable():
    declared = {"color": True, "duplex": False}
    rec = reconcile_capabilities(
        "printer-1",
        declared,
        observed=None,
        status=CapabilityReconciliationStatus.UNAVAILABLE,
    )
    assert rec.status == CapabilityReconciliationStatus.UNAVAILABLE
    assert rec.observed_capabilities is None


def test_declared_unsupported_observed_supported():
    declared = {"color": False}
    observed = {"color": True}
    rec = reconcile_capabilities(
        "printer-1",
        declared,
        observed,
        status=CapabilityReconciliationStatus.CONFLICT,
    )
    assert rec.status == CapabilityReconciliationStatus.CONFLICT


def test_declared_unknown_observed_supported():
    declared: dict[str, bool] = {}
    observed = {"color": True}
    rec = reconcile_capabilities(
        "printer-1",
        declared,
        observed,
        status=CapabilityReconciliationStatus.ACCEPTED,
    )
    assert rec.status == CapabilityReconciliationStatus.ACCEPTED


def test_declared_supported_observation_stale():
    declared = {"color": True, "duplex": False}
    observed = {"color": False}
    rec = reconcile_capabilities(
        "printer-1",
        declared,
        observed=observed,
        status=CapabilityReconciliationStatus.CONFLICT,
    )
    assert rec.status == CapabilityReconciliationStatus.CONFLICT
    assert rec.declared_capabilities == declared
    assert rec.observed_capabilities == observed


def test_reconciliation_preserves_provenance_and_timestamp():
    declared = {"color": True}
    observed = {"color": True}
    provenance = {"source": "test"}
    rec = reconcile_capabilities("printer-1", declared, observed, provenance=provenance)
    assert rec.provenance == provenance
    assert isinstance(rec.timestamp, datetime)


def test_capability_reconciliation_does_not_mutate_declared_capabilities():
    declared = {"duplex": False}
    observed = {"duplex": True}
    rec = reconcile_capabilities("printer-1", declared, observed)
    assert declared["duplex"] is False
    assert rec.declared_capabilities["duplex"] is False
