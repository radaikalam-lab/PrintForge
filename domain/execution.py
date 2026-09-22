from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ExecutionState(str, Enum):
    SUBMITTED = "SUBMITTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


class PrintExecution(BaseModel):
    execution_id: str
    job_id: str
    printer_id: str
    provider: str | None = None
    requested_operation: str
    accepted: bool = False
    timestamps: dict[str, datetime] = Field(default_factory=dict)
    provider_response: dict[str, Any] | None = None
    execution_state: ExecutionState = ExecutionState.SUBMITTED
    failure_information: dict[str, Any] | None = None
    provenance: dict[str, Any] = Field(default_factory=dict)
