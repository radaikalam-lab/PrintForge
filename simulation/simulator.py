import random
from datetime import UTC, datetime

from domain.capabilities import PrinterCapabilities
from domain.execution import ExecutionState, PrintExecution
from domain.job import PrintJob, PrintJobState
from domain.observation import PrinterObservation
from domain.printer import Printer, PrinterState
from domain.state_machines import validate_job_transition


class DeterministicPrinterSimulator:
    def __init__(self, seed: int | None = None):
        self._rng = random.Random(seed)
        self._printers: dict[str, Printer] = {}
        self._jobs: dict[str, PrintJob] = {}
        self._observations: dict[str, PrinterObservation] = {}
        self._executions: dict[str, PrintExecution] = {}
        self._latency_ms: int = 0
        self._failure_injection: bool = False
        self._paper_empty: dict[str, bool] = {}

    def set_latency(self, latency_ms: int) -> None:
        self._latency_ms = latency_ms

    def enable_failure_injection(self, enabled: bool) -> None:
        self._failure_injection = enabled

    def set_paper_empty(self, printer_id: str, empty: bool) -> None:
        self._paper_empty[printer_id] = empty

    def register_printer(self, printer: Printer) -> None:
        self._printers[printer.printer_id] = printer

    def _now(self) -> datetime:
        return datetime.now(UTC)

    async def discover(self) -> list[Printer]:
        if self._latency_ms:
            import asyncio
            await asyncio.sleep(self._latency_ms / 1000.0)
        return list(self._printers.values())

    async def get_identities(self) -> list[str]:
        return list(self._printers.keys())

    async def get_capabilities(self, printer_id: str) -> PrinterCapabilities:
        printer = self._printers.get(printer_id)
        if not printer:
            raise KeyError(f"Printer {printer_id} not found")
        return printer.capabilities

    async def observe(self, printer_id: str) -> PrinterObservation:
        printer = self._printers.get(printer_id)
        if not printer:
            raise KeyError(f"Printer {printer_id} not found")
        state = printer.state.value
        job_state = None
        for job in self._jobs.values():
            if job.resolved_printer == printer_id and job.state in (
                PrintJobState.SUBMITTED,
                PrintJobState.PROCESSING,
            ):
                job_state = job.state.value
                break
        consumables = {"paper": "empty" if self._paper_empty.get(printer_id, False) else "ok"}
        observation = PrinterObservation(
            printer_identity=printer.identity,
            printer_state=state,
            job_state=job_state,
            consumables=consumables,
            source="simulator",
            provider="SimulatorProvider",
            provenance={"simulator": True},
        )
        self._observations[printer_id] = observation
        return observation

    async def submit(self, job: PrintJob) -> PrintExecution:
        validate_job_transition(job.state, PrintJobState.SUBMITTED)
        job.state = PrintJobState.SUBMITTED
        if job.resolved_printer:
            job.resolved_printer = job.resolved_printer
        execution_id = f"exec-{self._rng.randint(1000, 9999)}"
        execution = PrintExecution(
            execution_id=execution_id,
            job_id=job.job_id,
            printer_id=job.resolved_printer or "",
            provider="SimulatorProvider",
            requested_operation="submit",
            accepted=True,
            timestamps={"submitted": self._now()},
            execution_state=ExecutionState.SUBMITTED,
            provenance={"simulator": True},
        )
        self._executions[execution_id] = execution
        self._jobs[job.job_id] = job
        if job.resolved_printer:
            printer = self._printers.get(job.resolved_printer)
            if printer:
                printer.state = PrinterState.PROCESSING
        return execution

    async def cancel(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if not job:
            return False
        validate_job_transition(job.state, PrintJobState.CANCELLED)
        job.state = PrintJobState.CANCELLED
        if job.resolved_printer:
            printer = self._printers.get(job.resolved_printer)
            if printer and printer.state == PrinterState.PROCESSING:
                printer.state = PrinterState.IDLE
        return True

    async def advance_job(self, job_id: str, target_state: PrintJobState) -> PrintJob:
        job = self._jobs.get(job_id)
        if not job:
            raise KeyError(f"Job {job_id} not found")
        validate_job_transition(job.state, target_state)
        job.state = target_state
        if target_state == PrintJobState.COMPLETED:
            for execution in self._executions.values():
                if execution.job_id == job_id:
                    execution.execution_state = ExecutionState.COMPLETED
                    execution.timestamps["completed"] = self._now()
                    break
            if job.resolved_printer:
                printer = self._printers.get(job.resolved_printer)
                if printer:
                    printer.state = PrinterState.IDLE
        elif target_state == PrintJobState.FAILED:
            for execution in self._executions.values():
                if execution.job_id == job_id:
                    execution.execution_state = ExecutionState.FAILED
                    execution.failure_information = {"reason": "simulated_failure"}
                    break
            if job.resolved_printer:
                printer = self._printers.get(job.resolved_printer)
                if printer:
                    printer.state = PrinterState.ERROR
        return job

    def get_job(self, job_id: str) -> PrintJob | None:
        return self._jobs.get(job_id)

    def get_execution(self, execution_id: str) -> PrintExecution | None:
        return self._executions.get(execution_id)
