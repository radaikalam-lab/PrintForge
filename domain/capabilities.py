from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


class PrinterCapabilities(BaseModel):
    media_formats: List[str] = Field(default_factory=list)
    media_types: List[str] = Field(default_factory=list)
    color: bool = False
    monochrome: bool = True
    duplex: bool = False
    resolutions: List[str] = Field(default_factory=list)
    printable_area: Optional[Dict[str, Any]] = None
    copies: bool = False
    finishing_capabilities: List[str] = Field(default_factory=list)
    supported_document_formats: List[str] = Field(default_factory=list)
    supported_protocols: List[str] = Field(default_factory=list)
