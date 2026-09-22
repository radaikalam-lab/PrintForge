from typing import Optional, Dict, Any, List
from persistence.interfaces import PrintJobRepository, PrinterRepository, ExecutionRepository, EventRepository
from domain.job import PrintJob, PrintJobState
from domain.printer import Printer, PrinterState
from domain.execution import PrintExecution, ExecutionState
from domain.events import DomainEvent
from datetime import datetime, UTC


class InMemoryPrintJobRepository(PrintJobRepository):
    def __init__(self):
        self._jobs: Dict[str, PrintJob] = {}

    async def save(self, job: PrintJob) -> None:
        self._jobs[job.job_id] = job

    async def get(self, job_id: str) -> Optional[PrintJob]:
        return self._jobs.get(job_id)

    async def list(self) -> List[PrintJob]:
        return list(self._jobs.values())

    async def delete(self, job_id: str) -> bool:
        return self._jobs.pop(job_id, None) is not None


class InMemoryPrinterRepository(PrinterRepository):
    def __init__(self):
        self._printers: Dict[str, Printer] = {}

    async def save(self, printer: Printer) -> None:
        self._printers[printer.printer_id] = printer

    async def get(self, printer_id: str) -> Optional[Printer]:
        return self._printers.get(printer_id)

    async def list(self) -> List[Printer]:
        return list(self._printers.values())

    async def delete(self, printer_id: str) -> bool:
        return self._printers.pop(printer_id, None) is not None


class InMemoryExecutionRepository(ExecutionRepository):
    def __init__(self):
        self._executions: Dict[str, PrintExecution] = {}

    async def save(self, execution: PrintExecution) -> None:
        self._executions[execution.execution_id] = execution

    async def get(self, execution_id: str) -> Optional[PrintExecution]:
        return self._executions.get(execution_id)

    async def list_by_job(self, job_id: str) -> List[PrintExecution]:
        return [e for e in self._executions.values() if e.job_id == job_id]


class InMemoryEventRepository(EventRepository):
    def __init__(self):
        self._events: List[DomainEvent] = []

    async def append(self, event: DomainEvent) -> None:
        self._events.append(event)

    async def get_events_for_job(self, job_id: str) -> List[DomainEvent]:
        return [e for e in self._events if hasattr(e, "job_id") and e.job_id == job_id]
