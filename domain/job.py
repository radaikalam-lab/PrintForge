from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PrintJobState(str, Enum):
    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    QUEUED = "QUEUED"
    SCHEDULED = "SCHEDULED"
    SUBMITTED = "SUBMITTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    ARCHIVED = "ARCHIVED"


class PrintJob(BaseModel):
    job_id: str
    source_document: str
    document_format: str
    requested_printer: str | None = None
    resolved_printer: str | None = None
    media: str | None = None
    page_size: str | None = None
    orientation: str | None = None
    copies: int = 1
    duplex: bool = False
    color_mode: str | None = None
    resolution: str | None = None
    scaling: str | None = None
    page_range: str | None = None
    priority: int = 0
    submission_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    requested_by: str | None = None
    policy_context: dict[str, Any] = Field(default_factory=dict)
    state: PrintJobState = PrintJobState.CREATED
    provenance: dict[str, Any] = Field(default_factory=dict)
