from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
from domain.job import PrintJob, PrintJobState
from domain.printer import Printer, PrinterState
from domain.capabilities import PrinterCapabilities
from domain.observation import PrinterObservation, EpistemicStatus
from domain.execution import PrintExecution
from domain.events import DomainEvent
from application.services import PrintJobService, PrinterService
from persistence.interfaces import (
    PrintJobRepository,
    PrinterRepository,
    ExecutionRepository,
    EventRepository,
)
from persistence.memory import (
    InMemoryPrintJobRepository,
    InMemoryPrinterRepository,
    InMemoryExecutionRepository,
    InMemoryEventRepository,
)
from providers.interfaces import (
    PrinterDiscoveryProvider,
    PrinterCapabilityProvider,
    PrinterObservationProvider,
    PrintSubmissionProvider,
    PrintCancellationProvider,
    SpoolProvider,
)
from server.errors import (
    PrintForgeError,
    InvalidRequestError,
    PrinterNotFoundError,
    JobNotFoundError,
    InvalidStateTransitionError,
    UnsupportedCapabilityError,
    ProviderFailureError,
    PolicyRejectionError,
    PersistenceError,
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
    location: Optional[str] = None


class PrinterCapabilitiesResponse(BaseModel):
    printer_id: str
    capabilities: Dict[str, Any]


class PrinterStatusResponse(BaseModel):
    printer_id: str
    status: str
    epistemic_status: str
    timestamp: Optional[str] = None
    retrieval_timestamp: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class JobModel(BaseModel):
    id: str
    requested_printer: Optional[str] = None
    resolved_printer: Optional[str] = None
    document_format: Optional[str] = None
    state: str
    copies: int = 1
    duplex: bool = False
    priority: int = 0
    submission_time: Optional[str] = None


class JobCreateRequest(BaseModel):
    job_id: str
    source_document: str
    document_format: str
    requested_printer: Optional[str] = None
    copies: int = 1
    duplex: bool = False
    priority: int = 0
    requested_by: Optional[str] = None


class JobEventResponse(BaseModel):
    job_id: str
    timestamp: str
    event_type: str
    provenance: Dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


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


def get_spool_provider() -> Optional[SpoolProvider]:
    return None


def get_print_job_service(
    job_repo: PrintJobRepository = Depends(get_job_repository),
    execution_repo: ExecutionRepository = Depends(get_execution_repository),
    event_repo: EventRepository = Depends(get_event_repository),
    submission_provider: PrintSubmissionProvider = Depends(get_submission_provider),
    spool_provider: Optional[SpoolProvider] = Depends(get_spool_provider),
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


@app.get("/api/v1/printers", response_model=List[PrinterModel])
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


@app.get("/api/v1/jobs", response_model=List[JobModel])
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


@app.get("/api/v1/jobs/{job_id}/events", response_model=List[JobEventResponse])
async def get_job_events(job_id: str, service: PrintJobService = Depends(get_print_job_service)):
    events = await service.get_events(job_id)
    return [
        JobEventResponse(
            job_id=e.job_id,
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