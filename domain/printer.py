from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

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
    location: str | None = None
    provider: str | None = None
    last_observation: dict[str, Any] | None = None
    provenance: dict[str, Any] = Field(default_factory=dict)
