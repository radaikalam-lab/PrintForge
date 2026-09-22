from pydantic import BaseModel, Field
from datetime import datetime, UTC
from typing import Optional, Dict, Any, List
from enum import Enum


class EpistemicStatus(str, Enum):
    DECLARED = "DECLARED"
    OBSERVED = "OBSERVED"
    DERIVED = "DERIVED"
    INFERRED = "INFERRED"
    ASSUMED = "ASSUMED"
    UNKNOWN = "UNKNOWN"
    CONTRADICTED = "CONTRADICTED"
    STALE = "STALE"


class PrinterObservation(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    printer_identity: str
    printer_state: str
    job_state: Optional[str] = None
    consumables: Optional[Dict[str, Any]] = None
    media_state: Optional[Dict[str, Any]] = None
    error_state: Optional[Dict[str, Any]] = None
    source: Optional[str] = None
    provider: Optional[str] = None
    provider_version: Optional[str] = None
    retrieval_timestamp: Optional[datetime] = None
    raw_provider_data: Optional[Dict[str, Any]] = None
    normalized_data: Optional[Dict[str, Any]] = None
    epistemic_status: EpistemicStatus = EpistemicStatus.OBSERVED
    provenance: Dict[str, Any] = Field(default_factory=dict)
