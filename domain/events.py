from pydantic import BaseModel, Field
from datetime import datetime, UTC
from typing import Optional, Dict, Any


class DomainEvent(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    provenance: Dict[str, Any] = Field(default_factory=dict)


class PrintJobCreated(DomainEvent):
    job_id: str
    requested_by: Optional[str] = None
    document_format: Optional[str] = None


class PrintJobValidated(DomainEvent):
    job_id: str
    validation_result: Dict[str, Any] = Field(default_factory=dict)


class PrintJobRejected(DomainEvent):
    job_id: str
    reason: str


class PrintJobQueued(DomainEvent):
    job_id: str
    queue_position: Optional[int] = None


class PrintJobScheduled(DomainEvent):
    job_id: str
    scheduled_time: Optional[datetime] = None
    printer_id: Optional[str] = None


class PrintJobSubmitted(DomainEvent):
    job_id: str
    execution_id: Optional[str] = None
    printer_id: Optional[str] = None


class PrintJobProcessing(DomainEvent):
    job_id: str
    execution_id: Optional[str] = None


class PrintJobCompleted(DomainEvent):
    job_id: str
    execution_id: Optional[str] = None
    provider_response: Optional[Dict[str, Any]] = None


class PrintJobCancelled(DomainEvent):
    job_id: str
    reason: Optional[str] = None


class PrintJobFailed(DomainEvent):
    job_id: str
    execution_id: Optional[str] = None
    failure_reason: str
    failure_information: Optional[Dict[str, Any]] = None


class PrinterDiscovered(DomainEvent):
    printer_id: str
    name: str
    protocol: str
    location: Optional[str] = None


class PrinterCapabilityObserved(DomainEvent):
    printer_id: str
    capabilities: Dict[str, Any] = Field(default_factory=dict)


class PrinterStatusObserved(DomainEvent):
    printer_id: str
    status: str
    details: Optional[Dict[str, Any]] = None


class PrinterErrorObserved(DomainEvent):
    printer_id: str
    error_state: Dict[str, Any] = Field(default_factory=dict)


class ProviderFailure(DomainEvent):
    provider: str
    operation: str
    error_message: str
    error_details: Optional[Dict[str, Any]] = None
