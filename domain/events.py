from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class DomainEvent(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    provenance: dict[str, Any] = Field(default_factory=dict)


class PrintJobCreated(DomainEvent):
    job_id: str
    requested_by: str | None = None
    document_format: str | None = None


class PrintJobValidated(DomainEvent):
    job_id: str
    validation_result: dict[str, Any] = Field(default_factory=dict)


class PrintJobRejected(DomainEvent):
    job_id: str
    reason: str


class PrintJobQueued(DomainEvent):
    job_id: str
    queue_position: int | None = None


class PrintJobScheduled(DomainEvent):
    job_id: str
    scheduled_time: datetime | None = None
    printer_id: str | None = None


class PrintJobSubmitted(DomainEvent):
    job_id: str
    execution_id: str | None = None
    printer_id: str | None = None


class PrintJobProcessing(DomainEvent):
    job_id: str
    execution_id: str | None = None


class PrintJobCompleted(DomainEvent):
    job_id: str
    execution_id: str | None = None
    provider_response: dict[str, Any] | None = None


class PrintJobCancelled(DomainEvent):
    job_id: str
    reason: str | None = None


class PrintJobFailed(DomainEvent):
    job_id: str
    execution_id: str | None = None
    failure_reason: str
    failure_information: dict[str, Any] | None = None


class PrinterDiscovered(DomainEvent):
    printer_id: str
    name: str
    protocol: str
    location: str | None = None


class PrinterCapabilityObserved(DomainEvent):
    printer_id: str
    capabilities: dict[str, Any] = Field(default_factory=dict)


class PrinterStatusObserved(DomainEvent):
    printer_id: str
    status: str
    details: dict[str, Any] | None = None


class PrinterErrorObserved(DomainEvent):
    printer_id: str
    error_state: dict[str, Any] = Field(default_factory=dict)


class ProviderFailure(DomainEvent):
    provider: str
    operation: str
    error_message: str
    error_details: dict[str, Any] | None = None
