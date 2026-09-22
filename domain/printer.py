from pydantic import BaseModel, Field
from datetime import datetime, UTC
from typing import Optional, Dict, Any, List
from enum import Enum
from domain.capabilities import PrinterCapabilities


class PrinterState(str, Enum):
    IDLE = "IDLE"
    PROCESSING = "PROCESSING"
    ERROR = "ERROR"
    OFFLINE = "OFFLINE"
    UNKNOWN = "UNKNOWN"


class Printer(BaseModel):
    printer_id: str
    name: str
    identity: str
    protocol: str
    capabilities: PrinterCapabilities
    state: PrinterState = PrinterState.UNKNOWN
    location: Optional[str] = None
    provider: Optional[str] = None
    last_observation: Optional[Dict[str, Any]] = None
    provenance: Dict[str, Any] = Field(default_factory=dict)
