from typing import Any

from domain.events import DomainEvent, PrintJobCreated
from domain.execution import PrintExecution
from domain.job import PrintJob, PrintJobState
from domain.printer import Printer
from persistence.interfaces import (
    EventRepository,
    ExecutionRepository,
    PrinterRepository,
    PrintJobRepository,
)
from providers.interfaces import (
    PrinterCapabilityProvider,
    PrinterDiscoveryProvider,
    PrinterObservationProvider,
    PrintSubmissionProvider,
    SpoolProvider,
)
from server.errors import (
    PrinterNotFoundError,
)


class PrintJobService:
    def __init__(
        self,
        job_repository: PrintJobRepository,
        execution_repository: ExecutionRepository,
        event_repository: EventRepository,
        submission_provider: PrintSubmissionProvider,
        spool_provider: SpoolProvider | None = None,
    ):
        self.job_repository = job_repository
        self.execution_repository = execution_repository
        self.event_repository = event_repository
        self.submission_provider = submission_provider
        self.spool_provider = spool_provider

    async def create_job(self, job: PrintJob) -> PrintJob:
        job.state = PrintJobState.CREATED
        await self.job_repository.save(job)
        event = PrintJobCreated(
            job_id=job.job_id,
            requested_by=job.requested_by,
            document_format=job.document_format,
            provenance=job.provenance,
        )
        await self.event_repository.append(event)
        return job

    async def validate_job(self, job: PrintJob) -> PrintJob:
        from domain.state_machines import validate_job_transition
        validate_job_transition(job.state, PrintJobState.VALIDATED)
        job.state = PrintJobState.VALIDATED
        await self.job_repository.save(job)
        from domain.events import PrintJobValidated
        event = PrintJobValidated(
            job_id=job.job_id,
            validation_result={},
            provenance=job.provenance,
        )
        await self.event_repository.append(event)
        return job

    async def submit_job(self, job: PrintJob) -> PrintExecution:
        from domain.state_machines import validate_job_transition
        validate_job_transition(job.state, PrintJobState.SUBMITTED)
        job.state = PrintJobState.SUBMITTED
        await self.job_repository.save(job)
        execution = await self.submission_provider.submit(job)
        await self.execution_repository.save(execution)
        from domain.events import PrintJobSubmitted
        event = PrintJobSubmitted(
            job_id=job.job_id,
            execution_id=execution.execution_id,
            printer_id=job.resolved_printer,
            provenance=job.provenance,
        )
        await self.event_repository.append(event)
        return execution

    async def cancel_job(self, job: PrintJob) -> PrintJob:
        from domain.state_machines import validate_job_transition
        validate_job_transition(job.state, PrintJobState.CANCELLED)
        job.state = PrintJobState.CANCELLED
        await self.job_repository.save(job)
        from domain.events import PrintJobCancelled
        event = PrintJobCancelled(
            job_id=job.job_id,
            provenance=job.provenance,
        )
        await self.event_repository.append(event)
        return job

    async def get_job(self, job_id: str) -> PrintJob | None:
        return await self.job_repository.get(job_id)

    async def list_jobs(self) -> list[PrintJob]:
        return await self.job_repository.list()

    async def get_events(self, job_id: str) -> list[DomainEvent]:
        return await self.event_repository.get_events_for_job(job_id)


class PrinterService:
    def __init__(
        self,
        printer_repository: PrinterRepository,
        discovery_provider: PrinterDiscoveryProvider,
        capability_provider: PrinterCapabilityProvider,
        observation_provider: PrinterObservationProvider,
        event_repository: EventRepository,
    ):
        self.printer_repository = printer_repository
        self.discovery_provider = discovery_provider
        self.capability_provider = capability_provider
        self.observation_provider = observation_provider
        self.event_repository = event_repository

    async def discover_printers(self) -> list[Printer]:
        printers = await self.discovery_provider.discover()
        for printer in printers:
            await self.printer_repository.save(printer)
            from domain.events import PrinterDiscovered
            event = PrinterDiscovered(
                printer_id=printer.printer_id,
                name=printer.name,
                protocol=printer.protocol,
                location=printer.location,
                provenance=printer.provenance,
            )
            await self.event_repository.append(event)
        return printers

    async def get_capabilities(self, printer_id: str) -> dict[str, Any]:
        printer = await self.printer_repository.get(printer_id)
        if not printer:
            raise PrinterNotFoundError(printer_id)
        caps = await self.capability_provider.get_capabilities(printer_id)
        from domain.events import PrinterCapabilityObserved
        event = PrinterCapabilityObserved(
            printer_id=printer_id,
            capabilities=caps.model_dump(),
            provenance={},
        )
        await self.event_repository.append(event)
        return caps.model_dump()

    async def get_status(self, printer_id: str) -> dict[str, Any]:
        printer = await self.printer_repository.get(printer_id)
        if not printer:
            raise PrinterNotFoundError(printer_id)
        observation = await self.observation_provider.observe(printer_id)
        from domain.events import PrinterStatusObserved
        event = PrinterStatusObserved(
            printer_id=printer_id,
            status=observation.printer_state,
            details=observation.normalized_data,
            provenance=observation.provenance,
        )
        await self.event_repository.append(event)
        return {
            "printer_id": printer_id,
            "status": observation.printer_state,
            "timestamp": observation.timestamp.isoformat(),
            "retrieval_timestamp": observation.retrieval_timestamp.isoformat() if observation.retrieval_timestamp else None,
            "epistemic_status": observation.epistemic_status.value,
            "details": observation.normalized_data,
        }
