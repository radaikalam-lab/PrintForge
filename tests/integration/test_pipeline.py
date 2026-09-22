import asyncio

import pytest

from application.services import PrintJobService
from domain.capabilities import PrinterCapabilities
from domain.execution import PrintExecution
from domain.job import PrintJob, PrintJobState
from domain.printer import Printer, PrinterState
from persistence.memory import (
    InMemoryEventRepository,
    InMemoryExecutionRepository,
    InMemoryPrintJobRepository,
)
from providers.interfaces import PrintSubmissionProvider
from simulation.simulator import DeterministicPrinterSimulator


class FakeSubmissionProvider(PrintSubmissionProvider):
    capability_declaration: dict = {}
    supported_operations: list = []
    version: str = "1.0.0"
    deterministic_identity: str = "fake"
    provenance: dict = {}

    def __init__(self):
        self.submitted: list = []

    async def submit(self, job: PrintJob) -> PrintExecution:
        from domain.execution import ExecutionState

        execution = PrintExecution(
            execution_id=f"exec-{job.job_id}",
            job_id=job.job_id,
            printer_id=job.resolved_printer or "",
            provider="fake",
            requested_operation="submit",
            accepted=True,
            execution_state=ExecutionState.SUBMITTED,
            provenance={"fake": True},
        )
        self.submitted.append(execution)
        return execution


@pytest.fixture
def service():
    simulator = DeterministicPrinterSimulator(seed=123)
    caps = PrinterCapabilities(color=True, duplex=False, supported_document_formats=["pdf"])
    printer = Printer(
        printer_id="printer-1",
        name="Sim",
        identity="urn:printer:sim",
        protocol="ipp",
        capabilities=caps,
        state=PrinterState.IDLE,
    )
    simulator.register_printer(printer)
    submission_provider = FakeSubmissionProvider()
    service = PrintJobService(
        job_repository=InMemoryPrintJobRepository(),
        execution_repository=InMemoryExecutionRepository(),
        event_repository=InMemoryEventRepository(),
        spool_provider=None,
        submission_provider=submission_provider,
    )
    return service, simulator, submission_provider


def test_create_and_submit_job(service):
    svc, simulator, submission_provider = service
    job = PrintJob(
        job_id="job-1",
        source_document="file:///tmp/doc.pdf",
        document_format="pdf",
        resolved_printer="printer-1",
    )
    job = asyncio.run(svc.create_job(job))
    assert job.state == PrintJobState.CREATED
    job = asyncio.run(svc.validate_job(job))
    assert job.state == PrintJobState.VALIDATED
    job.state = PrintJobState.QUEUED
    job.state = PrintJobState.SCHEDULED
    execution = asyncio.run(svc.submit_job(job))
    assert execution.accepted is True
    assert len(submission_provider.submitted) == 1
