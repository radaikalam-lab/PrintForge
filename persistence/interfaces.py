from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime, UTC
from domain.job import PrintJob
from domain.printer import Printer
from domain.execution import PrintExecution
from domain.events import DomainEvent


class PrintJobRepository(ABC):
    @abstractmethod
    async def save(self, job: PrintJob) -> None:
        pass

    @abstractmethod
    async def get(self, job_id: str) -> Optional[PrintJob]:
        pass

    @abstractmethod
    async def list(self) -> List[PrintJob]:
        pass

    @abstractmethod
    async def delete(self, job_id: str) -> bool:
        pass


class PrinterRepository(ABC):
    @abstractmethod
    async def save(self, printer: Printer) -> None:
        pass

    @abstractmethod
    async def get(self, printer_id: str) -> Optional[Printer]:
        pass

    @abstractmethod
    async def list(self) -> List[Printer]:
        pass

    @abstractmethod
    async def delete(self, printer_id: str) -> bool:
        pass


class ExecutionRepository(ABC):
    @abstractmethod
    async def save(self, execution: PrintExecution) -> None:
        pass

    @abstractmethod
    async def get(self, execution_id: str) -> Optional[PrintExecution]:
        pass

    @abstractmethod
    async def list_by_job(self, job_id: str) -> List[PrintExecution]:
        pass


class EventRepository(ABC):
    @abstractmethod
    async def append(self, event: DomainEvent) -> None:
        pass

    @abstractmethod
    async def get_events_for_job(self, job_id: str) -> List[DomainEvent]:
        pass
