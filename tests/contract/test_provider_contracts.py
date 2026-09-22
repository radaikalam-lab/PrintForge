import pytest

from providers.interfaces import (
    DocumentTransformProvider,
    PrintCancellationProvider,
    PrinterCapabilityProvider,
    PrinterDiscoveryProvider,
    PrinterObservationProvider,
    PrintServerProvider,
    PrintSubmissionProvider,
    SpoolProvider,
)


def test_provider_interfaces_are_abstract():
    for cls in [
        PrinterDiscoveryProvider,
        PrinterCapabilityProvider,
        PrinterObservationProvider,
        PrintSubmissionProvider,
        PrintCancellationProvider,
        SpoolProvider,
        DocumentTransformProvider,
        PrintServerProvider,
    ]:
        with pytest.raises(TypeError):
            cls()


def test_provider_has_abstract_methods():
    assert hasattr(PrinterDiscoveryProvider, "discover")
    assert hasattr(PrinterCapabilityProvider, "get_capabilities")
    assert hasattr(PrinterObservationProvider, "observe")
    assert hasattr(PrintSubmissionProvider, "submit")
    assert hasattr(PrintCancellationProvider, "cancel")
    assert hasattr(SpoolProvider, "store")
    assert hasattr(DocumentTransformProvider, "transform")
    assert hasattr(PrintServerProvider, "status")
