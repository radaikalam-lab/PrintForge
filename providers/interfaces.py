from abc import ABC, abstractmethod
from typing import List, Dict, Any
from domain.printer import Printer
from domain.capabilities import PrinterCapabilities
from domain.observation import PrinterObservation
from domain.execution import PrintExecution
from domain.job import PrintJob


class PrinterDiscoveryProvider(ABC):
    capability_declaration: Dict[str, Any]
    supported_operations: List[str]
    version: str
    deterministic_identity: str
    provenance: Dict[str, Any]
    failure_semantics: str
    timeout_behavior: str
    retry_semantics: str
    idempotency_semantics: str

    @abstractmethod
    async def discover(self) -> List[Printer]:
        pass

    @abstractmethod
    async def get_identities(self) -> List[str]:
        pass


class PrinterCapabilityProvider(ABC):
    capability_declaration: Dict[str, Any]
    supported_operations: List[str]
    version: str
    deterministic_identity: str
    provenance: Dict[str, Any]

    @abstractmethod
    async def get_capabilities(self, printer_id: str) -> PrinterCapabilities:
        pass


class PrinterObservationProvider(ABC):
    capability_declaration: Dict[str, Any]
    supported_operations: List[str]
    version: str
    deterministic_identity: str
    provenance: Dict[str, Any]

    @abstractmethod
    async def observe(self, printer_id: str) -> PrinterObservation:
        pass


class PrintSubmissionProvider(ABC):
    capability_declaration: Dict[str, Any]
    supported_operations: List[str]
    version: str
    deterministic_identity: str
    provenance: Dict[str, Any]

    @abstractmethod
    async def submit(self, job: PrintJob) -> PrintExecution:
        pass


class PrintCancellationProvider(ABC):
    capability_declaration: Dict[str, Any]
    supported_operations: List[str]
    version: str
    deterministic_identity: str
    provenance: Dict[str, Any]

    @abstractmethod
    async def cancel(self, job_id: str) -> bool:
        pass


class PrinterControlProvider(ABC):
    capability_declaration: Dict[str, Any]
    supported_operations: List[str]
    version: str
    deterministic_identity: str
    provenance: Dict[str, Any]

    @abstractmethod
    async def control(self, printer_id: str, operation: str) -> PrintExecution:
        pass


class SpoolProvider(ABC):
    capability_declaration: Dict[str, Any]
    supported_operations: List[str]
    version: str
    deterministic_identity: str
    provenance: Dict[str, Any]

    @abstractmethod
    async def store(self, artifact: bytes, metadata: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def retrieve(self, artifact_id: str) -> bytes:
        pass

    @abstractmethod
    async def delete(self, artifact_id: str) -> bool:
        pass


class DocumentTransformProvider(ABC):
    capability_declaration: Dict[str, Any]
    supported_operations: List[str]
    version: str
    deterministic_identity: str
    provenance: Dict[str, Any]

    @abstractmethod
    async def transform(self, document: bytes, source_format: str, target_format: str) -> bytes:
        pass


class PrintServerProvider(ABC):
    capability_declaration: Dict[str, Any]
    supported_operations: List[str]
    version: str
    deterministic_identity: str
    provenance: Dict[str, Any]

    @abstractmethod
    async def status(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def submit_job(self, job_spec: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def cancel_job(self, job_id: str) -> bool:
        pass
