from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from application.services import PrinterService, PrintJobService
from domain.job import PrintJob, PrintJobState
from persistence.interfaces import (
    EventRepository,
    ExecutionRepository,
    PrinterRepository,
    PrintJobRepository,
)
from persistence.memory import (
    InMemoryEventRepository,
    InMemoryExecutionRepository,
    InMemoryPrinterRepository,
    InMemoryPrintJobRepository,
)
from providers.interfaces import (
    PrinterCapabilityProvider,
    PrinterDiscoveryProvider,
    PrinterObservationProvider,
    PrintSubmissionProvider,
    SpoolProvider,
)
from server.errors import (
    InvalidStateTransitionError,
    JobNotFoundError,
    PrinterNotFoundError,
    PrintForgeError,
    map_to_http,
)

app = FastAPI(
    title="PrintForge API",
    description="Open, Local-First Printing Control Plane",
    version="0.1.0",
)


# --- Pydantic response models ---


class PrinterModel(BaseModel):
    id: str
    name: str
    protocol: str
    state: str
    location: str | None = None


class PrinterCapabilitiesResponse(BaseModel):
    printer_id: str
    capabilities: dict[str, Any]


class PrinterStatusResponse(BaseModel):
    printer_id: str
    status: str
    epistemic_status: str
    timestamp: str | None = None
    retrieval_timestamp: str | None = None
    details: dict[str, Any] | None = None


class JobModel(BaseModel):
    id: str
    requested_printer: str | None = None
    resolved_printer: str | None = None
    document_format: str | None = None
    state: str
    copies: int = 1
    duplex: bool = False
    priority: int = 0
    submission_time: str | None = None


class JobCreateRequest(BaseModel):
    job_id: str
    source_document: str
    document_format: str
    requested_printer: str | None = None
    copies: int = 1
    duplex: bool = False
    priority: int = 0
    requested_by: str | None = None


class JobEventResponse(BaseModel):
    job_id: str
    timestamp: str
    event_type: str
    provenance: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


# --- Dependency wiring ---


def get_job_repository() -> PrintJobRepository:
    return InMemoryPrintJobRepository()


def get_printer_repository() -> PrinterRepository:
    return InMemoryPrinterRepository()


def get_execution_repository() -> ExecutionRepository:
    return InMemoryExecutionRepository()


def get_event_repository() -> EventRepository:
    return InMemoryEventRepository()


def get_discovery_provider() -> PrinterDiscoveryProvider:
    raise NotImplementedError("Discovery provider not wired in Phase 3")


def get_capability_provider() -> PrinterCapabilityProvider:
    raise NotImplementedError("Capability provider not wired in Phase 3")


def get_observation_provider() -> PrinterObservationProvider:
    raise NotImplementedError("Observation provider not wired in Phase 3")


def get_submission_provider() -> PrintSubmissionProvider:
    raise NotImplementedError("Submission provider not wired in Phase 3")


def get_spool_provider() -> SpoolProvider | None:
    return None


def get_print_job_service(
    job_repo: PrintJobRepository = Depends(get_job_repository),
    execution_repo: ExecutionRepository = Depends(get_execution_repository),
    event_repo: EventRepository = Depends(get_event_repository),
    submission_provider: PrintSubmissionProvider = Depends(get_submission_provider),
    spool_provider: SpoolProvider | None = Depends(get_spool_provider),
) -> PrintJobService:
    return PrintJobService(
        job_repository=job_repo,
        execution_repository=execution_repo,
        event_repository=event_repo,
        submission_provider=submission_provider,
        spool_provider=spool_provider,
    )


def get_printer_service(
    printer_repo: PrinterRepository = Depends(get_printer_repository),
    event_repo: EventRepository = Depends(get_event_repository),
    discovery_provider: PrinterDiscoveryProvider = Depends(get_discovery_provider),
    capability_provider: PrinterCapabilityProvider = Depends(get_capability_provider),
    observation_provider: PrinterObservationProvider = Depends(get_observation_provider),
) -> PrinterService:
    return PrinterService(
        printer_repository=printer_repo,
        discovery_provider=discovery_provider,
        capability_provider=capability_provider,
        observation_provider=observation_provider,
        event_repository=event_repo,
    )


# --- Exception handler ---


@app.exception_handler(PrintForgeError)
async def printforge_error_handler(request, exc: PrintForgeError):
    raise map_to_http(exc)


@app.exception_handler(NotImplementedError)
async def not_implemented_error_handler(request, exc: NotImplementedError):
    raise HTTPException(status_code=501, detail={"code": "NOT_IMPLEMENTED", "message": str(exc)})


# --- Versioned routes ---


@app.get("/api/v1/printers", response_model=list[PrinterModel])
async def list_printers(service: PrinterService = Depends(get_printer_service)):
    printers = await service.discover_printers()
    return [
        PrinterModel(
            id=p.printer_id,
            name=p.name,
            protocol=p.protocol,
            state=p.state.value,
            location=p.location,
        )
        for p in printers
    ]


@app.get("/api/v1/printers/{printer_id}", response_model=PrinterModel)
async def get_printer(printer_id: str, service: PrinterService = Depends(get_printer_service)):
    printers = await service.discover_printers()
    for p in printers:
        if p.printer_id == printer_id:
            return PrinterModel(
                id=p.printer_id,
                name=p.name,
                protocol=p.protocol,
                state=p.state.value,
                location=p.location,
            )
    raise PrinterNotFoundError(printer_id)


@app.get("/api/v1/printers/{printer_id}/capabilities", response_model=PrinterCapabilitiesResponse)
async def get_printer_capabilities(printer_id: str, service: PrinterService = Depends(get_printer_service)):
    caps = await service.get_capabilities(printer_id)
    return PrinterCapabilitiesResponse(printer_id=printer_id, capabilities=caps)


@app.get("/api/v1/printers/{printer_id}/status", response_model=PrinterStatusResponse)
async def get_printer_status(printer_id: str, service: PrinterService = Depends(get_printer_service)):
    status = await service.get_status(printer_id)
    return PrinterStatusResponse(**status)


@app.post("/api/v1/jobs", response_model=JobModel)
async def create_job(request: JobCreateRequest, service: PrintJobService = Depends(get_print_job_service)):
    job = PrintJob(
        job_id=request.job_id,
        source_document=request.source_document,
        document_format=request.document_format,
        requested_printer=request.requested_printer,
        copies=request.copies,
        duplex=request.duplex,
        priority=request.priority,
        requested_by=request.requested_by,
    )
    job = await service.create_job(job)
    return JobModel(
        id=job.job_id,
        requested_printer=job.requested_printer,
        resolved_printer=job.resolved_printer,
        document_format=job.document_format,
        state=job.state.value,
        copies=job.copies,
        duplex=job.duplex,
        priority=job.priority,
        submission_time=job.submission_time.isoformat(),
    )


@app.get("/api/v1/jobs", response_model=list[JobModel])
async def list_jobs(service: PrintJobService = Depends(get_print_job_service)):
    jobs = await service.list_jobs()
    return [
        JobModel(
            id=j.job_id,
            requested_printer=j.requested_printer,
            resolved_printer=j.resolved_printer,
            document_format=j.document_format,
            state=j.state.value,
            copies=j.copies,
            duplex=j.duplex,
            priority=j.priority,
            submission_time=j.submission_time.isoformat(),
        )
        for j in jobs
    ]


@app.get("/api/v1/jobs/{job_id}", response_model=JobModel)
async def get_job(job_id: str, service: PrintJobService = Depends(get_print_job_service)):
    job = await service.get_job(job_id)
    if not job:
        raise JobNotFoundError(job_id)
    return JobModel(
        id=job.job_id,
        requested_printer=job.requested_printer,
        resolved_printer=job.resolved_printer,
        document_format=job.document_format,
        state=job.state.value,
        copies=job.copies,
        duplex=job.duplex,
        priority=job.priority,
        submission_time=job.submission_time.isoformat(),
    )


@app.post("/api/v1/jobs/{job_id}/cancel", response_model=JobModel)
async def cancel_job(job_id: str, service: PrintJobService = Depends(get_print_job_service)):
    job = await service.get_job(job_id)
    if not job:
        raise JobNotFoundError(job_id)
    try:
        job = await service.cancel_job(job)
    except ValueError as exc:
        raise InvalidStateTransitionError(job.state.value, PrintJobState.CANCELLED.value) from exc
    return JobModel(
        id=job.job_id,
        requested_printer=job.requested_printer,
        resolved_printer=job.resolved_printer,
        document_format=job.document_format,
        state=job.state.value,
        copies=job.copies,
        duplex=job.duplex,
        priority=job.priority,
        submission_time=job.submission_time.isoformat(),
    )


@app.get("/api/v1/jobs/{job_id}/events", response_model=list[JobEventResponse])
async def get_job_events(job_id: str, service: PrintJobService = Depends(get_print_job_service)):
    events = await service.get_events(job_id)
    return [
        JobEventResponse(
            job_id=e.job_id,  # type: ignore[attr-defined]
            timestamp=e.timestamp.isoformat(),
            event_type=type(e).__name__,
            provenance=e.provenance,
        )
        for e in events
    ]


# Health check
@app.get("/health")
async def health():
    return {"status": "ok"}
