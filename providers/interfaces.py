from abc import ABC, abstractmethod
from typing import Any

from domain.capabilities import PrinterCapabilities
from domain.execution import PrintExecution
from domain.job import PrintJob
from domain.observation import PrinterObservation
from domain.printer import Printer


class PrinterDiscoveryProvider(ABC):
    capability_declaration: dict[str, Any]
    supported_operations: list[str]
    version: str
    deterministic_identity: str
    provenance: dict[str, Any]
    failure_semantics: str
    timeout_behavior: str
    retry_semantics: str
    idempotency_semantics: str

    @abstractmethod
    async def discover(self) -> list[Printer]:
        pass

    @abstractmethod
    async def get_identities(self) -> list[str]:
        pass


class PrinterCapabilityProvider(ABC):
    capability_declaration: dict[str, Any]
    supported_operations: list[str]
    version: str
    deterministic_identity: str
    provenance: dict[str, Any]

    @abstractmethod
    async def get_capabilities(self, printer_id: str) -> PrinterCapabilities:
        pass


class PrinterObservationProvider(ABC):
    capability_declaration: dict[str, Any]
    supported_operations: list[str]
    version: str
    deterministic_identity: str
    provenance: dict[str, Any]

    @abstractmethod
    async def observe(self, printer_id: str) -> PrinterObservation:
        pass


class PrintSubmissionProvider(ABC):
    capability_declaration: dict[str, Any]
    supported_operations: list[str]
    version: str
    deterministic_identity: str
    provenance: dict[str, Any]

    @abstractmethod
    async def submit(self, job: PrintJob) -> PrintExecution:
        pass


class PrintCancellationProvider(ABC):
    capability_declaration: dict[str, Any]
    supported_operations: list[str]
    version: str
    deterministic_identity: str
    provenance: dict[str, Any]

    @abstractmethod
    async def cancel(self, job_id: str) -> bool:
        pass


class PrinterControlProvider(ABC):
    capability_declaration: dict[str, Any]
    supported_operations: list[str]
    version: str
    deterministic_identity: str
    provenance: dict[str, Any]

    @abstractmethod
    async def control(self, printer_id: str, operation: str) -> PrintExecution:
        pass


class SpoolProvider(ABC):
    capability_declaration: dict[str, Any]
    supported_operations: list[str]
    version: str
    deterministic_identity: str
    provenance: dict[str, Any]

    @abstractmethod
    async def store(self, artifact: bytes, metadata: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def retrieve(self, artifact_id: str) -> bytes:
        pass

    @abstractmethod
    async def delete(self, artifact_id: str) -> bool:
        pass


class DocumentTransformProvider(ABC):
    capability_declaration: dict[str, Any]
    supported_operations: list[str]
    version: str
    deterministic_identity: str
    provenance: dict[str, Any]

    @abstractmethod
    async def transform(self, document: bytes, source_format: str, target_format: str) -> bytes:
        pass


class PrintServerProvider(ABC):
    capability_declaration: dict[str, Any]
    supported_operations: list[str]
    version: str
    deterministic_identity: str
    provenance: dict[str, Any]

    @abstractmethod
    async def status(self) -> dict[str, Any]:
        pass

    @abstractmethod
    async def submit_job(self, job_spec: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def cancel_job(self, job_id: str) -> bool:
        pass
