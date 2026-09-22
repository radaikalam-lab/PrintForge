from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CapabilityReconciliationStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    ACCEPTED_WITH_STALE_EVIDENCE = "ACCEPTED_WITH_STALE_EVIDENCE"
    CONFLICT = "CONFLICT"
    UNRESOLVED = "UNRESOLVED"
    UNAVAILABLE = "UNAVAILABLE"


class CapabilityReconciliation(BaseModel):
    printer_id: str
    declared_capabilities: dict[str, Any]
    observed_capabilities: dict[str, Any] | None = None
    status: CapabilityReconciliationStatus = CapabilityReconciliationStatus.UNRESOLVED
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    provenance: dict[str, Any] = Field(default_factory=dict)


def reconcile_capabilities(
    printer_id: str,
    declared: dict[str, Any],
    observed: dict[str, Any] | None = None,
    status: CapabilityReconciliationStatus | None = None,
    provenance: dict[str, Any] | None = None,
) -> CapabilityReconciliation:
    if status is None:
        status = CapabilityReconciliationStatus.UNRESOLVED
    return CapabilityReconciliation(
        printer_id=printer_id,
        declared_capabilities=dict(declared),
        observed_capabilities=dict(observed) if observed is not None else None,
        status=status,
        provenance=provenance or {},
    )


class PrinterCapabilities(BaseModel):
    media_formats: list[str] = Field(default_factory=list)
    media_types: list[str] = Field(default_factory=list)
    color: bool = False
    monochrome: bool = True
    duplex: bool = False
    resolutions: list[str] = Field(default_factory=list)
    printable_area: dict[str, Any] | None = None
    copies: bool = False
    finishing_capabilities: list[str] = Field(default_factory=list)
    supported_document_formats: list[str] = Field(default_factory=list)
    supported_protocols: list[str] = Field(default_factory=list)
