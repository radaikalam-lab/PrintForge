from fastapi.testclient import TestClient

from application.services import PrinterService, PrintJobService
from domain.capabilities import PrinterCapabilities
from domain.observation import EpistemicStatus, PrinterObservation
from domain.printer import Printer, PrinterState
from persistence.memory import (
    InMemoryEventRepository,
    InMemoryExecutionRepository,
    InMemoryPrinterRepository,
    InMemoryPrintJobRepository,
)
from server.api import app
from tests.helpers.fake_providers import (
    FakeCapabilityProvider,
    FakeDiscoveryProvider,
    FakeObservationProvider,
    FakeSubmissionProvider,
)


class SharedTestState:
    printer_repo = InMemoryPrinterRepository()
    job_repo = InMemoryPrintJobRepository()
    execution_repo = InMemoryExecutionRepository()
    event_repo = InMemoryEventRepository()


def _build_printer_service():
    caps = PrinterCapabilities(
        color=True,
        duplex=False,
        supported_document_formats=["pdf"],
        supported_protocols=["ipp"],
    )
    printer = Printer(
        printer_id="printer-1",
        name="Demo Printer",
        identity="urn:printer:demo:1",
        protocol="ipp",
        capabilities=caps,
        state=PrinterState.IDLE,
    )
    import asyncio
    asyncio.run(SharedTestState.printer_repo.save(printer))
    discovery = FakeDiscoveryProvider([printer])
    capability = FakeCapabilityProvider({"printer-1": caps})
    observation = PrinterObservation(
        printer_identity=printer.identity,
        printer_state=PrinterState.IDLE.value,
        provider="fake",
        epistemic_status=EpistemicStatus.OBSERVED,
    )
    obs_provider = FakeObservationProvider(observation)
    return PrinterService(
        printer_repository=SharedTestState.printer_repo,
        discovery_provider=discovery,
        capability_provider=capability,
        observation_provider=obs_provider,
        event_repository=SharedTestState.event_repo,
    )


def _build_job_service():
    submission = FakeSubmissionProvider()
    return PrintJobService(
        job_repository=SharedTestState.job_repo,
        execution_repository=SharedTestState.execution_repo,
        event_repository=SharedTestState.event_repo,
        submission_provider=submission,
    )


def _override_dependencies():
    from server.api import (
        get_print_job_service,
        get_printer_service,
    )
    app.dependency_overrides[get_printer_service] = _build_printer_service
    app.dependency_overrides[get_print_job_service] = _build_job_service


def test_health():
    _override_dependencies()
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_printers():
    _override_dependencies()
    client = TestClient(app)
    response = client.get("/api/v1/printers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "id" in data[0]


def test_get_printer():
    _override_dependencies()
    client = TestClient(app)
    response = client.get("/api/v1/printers/printer-1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "printer-1"


def test_get_printer_not_found():
    _override_dependencies()
    client = TestClient(app)
    response = client.get("/api/v1/printers/unknown")
    assert response.status_code == 404


def test_get_printer_capabilities():
    _override_dependencies()
    client = TestClient(app)
    response = client.get("/api/v1/printers/printer-1/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert data["printer_id"] == "printer-1"
    assert "capabilities" in data


def test_get_printer_status():
    _override_dependencies()
    client = TestClient(app)
    response = client.get("/api/v1/printers/printer-1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["printer_id"] == "printer-1"
    assert "status" in data


def test_create_job():
    _override_dependencies()
    client = TestClient(app)
    response = client.post(
        "/api/v1/jobs",
        json={
            "job_id": "job-1",
            "source_document": "file:///tmp/test.pdf",
            "document_format": "pdf",
            "requested_printer": "printer-1",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "job-1"
    assert data["state"] == "CREATED"


def test_list_jobs():
    _override_dependencies()
    client = TestClient(app)
    client.post(
        "/api/v1/jobs",
        json={
            "job_id": "job-list-1",
            "source_document": "file:///tmp/test.pdf",
            "document_format": "pdf",
        },
    )
    response = client.get("/api/v1/jobs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_job():
    _override_dependencies()
    client = TestClient(app)
    client.post(
        "/api/v1/jobs",
        json={
            "job_id": "job-get-1",
            "source_document": "file:///tmp/test.pdf",
            "document_format": "pdf",
        },
    )
    response = client.get("/api/v1/jobs/job-get-1")
    assert response.status_code == 200
    assert response.json()["id"] == "job-get-1"


def test_cancel_job():
    _override_dependencies()
    client = TestClient(app)
    client.post(
        "/api/v1/jobs",
        json={
            "job_id": "job-cancel-1",
            "source_document": "file:///tmp/test.pdf",
            "document_format": "pdf",
        },
    )
    response = client.post("/api/v1/jobs/job-cancel-1/cancel")
    assert response.status_code == 200
    assert response.json()["state"] == "CANCELLED"


def test_get_job_events():
    _override_dependencies()
    client = TestClient(app)
    client.post(
        "/api/v1/jobs",
        json={
            "job_id": "job-events-1",
            "source_document": "file:///tmp/test.pdf",
            "document_format": "pdf",
        },
    )
    response = client.get("/api/v1/jobs/job-events-1/events")
    assert response.status_code == 200
    events = response.json()
    assert isinstance(events, list)
    assert len(events) >= 1
