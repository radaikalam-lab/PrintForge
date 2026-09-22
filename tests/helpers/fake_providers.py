
from domain.capabilities import PrinterCapabilities
from domain.execution import ExecutionState, PrintExecution
from domain.job import PrintJob
from domain.observation import PrinterObservation
from domain.printer import Printer
from providers.interfaces import (
    PrintCancellationProvider,
    PrinterCapabilityProvider,
    PrinterDiscoveryProvider,
    PrinterObservationProvider,
    PrintSubmissionProvider,
)


class FakeDiscoveryProvider(PrinterDiscoveryProvider):
    def __init__(self, printers: list[Printer]):
        self._printers = printers

    async def discover(self) -> list[Printer]:
        return list(self._printers)

    async def get_identities(self) -> list[str]:
        return [p.printer_id for p in self._printers]


class FakeCapabilityProvider(PrinterCapabilityProvider):
    def __init__(self, capabilities_map: dict):
        self._capabilities = capabilities_map

    async def get_capabilities(self, printer_id: str) -> PrinterCapabilities:
        return self._capabilities.get(printer_id, PrinterCapabilities())


class FakeObservationProvider(PrinterObservationProvider):
    def __init__(self, observation: PrinterObservation):
        self._observation = observation

    async def observe(self, printer_id: str) -> PrinterObservation:
        return self._observation


class FakeSubmissionProvider(PrintSubmissionProvider):
    def __init__(self):
        self.submitted: list[PrintExecution] = []

    async def submit(self, job: PrintJob) -> PrintExecution:
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


class FakeCancellationProvider(PrintCancellationProvider):
    def __init__(self):
        self.cancelled: list[str] = []

    async def cancel(self, job_id: str) -> bool:
        self.cancelled.append(job_id)
        return True
