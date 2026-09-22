from pydantic import BaseModel, Field
from datetime import datetime, UTC
from typing import Optional, Dict, Any, List
from enum import Enum


class PrintJobState(str, Enum):
    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    QUEUED = "QUEUED"
    SCHEDULED = "SCHEDULED"
    SUBMITTED = "SUBMITTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class PrintJob(BaseModel):
    job_id: str
    source_document: str
    document_format: str
    requested_printer: Optional[str] = None
    resolved_printer: Optional[str] = None
    media: Optional[str] = None
    page_size: Optional[str] = None
    orientation: Optional[str] = None
    copies: int = 1
    duplex: bool = False
    color_mode: Optional[str] = None
    resolution: Optional[str] = None
    scaling: Optional[str] = None
    page_range: Optional[str] = None
    priority: int = 0
    submission_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    requested_by: Optional[str] = None
    policy_context: Dict[str, Any] = Field(default_factory=dict)
    state: PrintJobState = PrintJobState.CREATED
    provenance: Dict[str, Any] = Field(default_factory=dict)
