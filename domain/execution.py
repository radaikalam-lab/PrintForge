from pydantic import BaseModel, Field
from datetime import datetime, UTC
from typing import Optional, Dict, Any, List
from enum import Enum


class ExecutionState(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class PrintExecution(BaseModel):
    execution_id: str
    job_id: str
    printer_id: str
    provider: Optional[str] = None
    requested_operation: str
    accepted: bool = False
    timestamps: Dict[str, datetime] = Field(default_factory=dict)
    provider_response: Optional[Dict[str, Any]] = None
    execution_state: ExecutionState = ExecutionState.PENDING
    failure_information: Optional[Dict[str, Any]] = None
    provenance: Dict[str, Any] = Field(default_factory=dict)
