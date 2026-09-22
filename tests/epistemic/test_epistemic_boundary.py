import asyncio
from datetime import UTC, datetime, timedelta

from application.services import PrinterService, PrintJobService
from domain.capabilities import PrinterCapabilities
from domain.job import PrintJob, PrintJobState
from domain.observation import (
    EpistemicStatus,
    FreshnessPolicy,
    PrinterObservation,
    observation_age_seconds,
    qualify_observation,
)
from domain.printer import Printer, PrinterState
from persistence.memory import (
    InMemoryEventRepository,
    InMemoryExecutionRepository,
    InMemoryPrinterRepository,
    InMemoryPrintJobRepository,
)
from tests.helpers.fake_providers import (
    FakeCapabilityProvider,
    FakeDiscoveryProvider,
    FakeObservationProvider,
    FakeSubmissionProvider,
)


def asyncio_await(coro):
    return asyncio.run(coro)


def test_observation_epistemic_status_is_exposed():
    event_repo = InMemoryEventRepository()
    printer_repo = InMemoryPrinterRepository()

    caps = PrinterCapabilities(color=True, duplex=False, supported_document_formats=["pdf"])
    printer = Printer(
        printer_id="printer-1",
        name="Epistemic Printer",
        identity="urn:printer:epistemic:1",
        protocol="ipp",
        capabilities=caps,
        state=PrinterState.IDLE,
    )
    asyncio_await(printer_repo.save(printer))

    observation = PrinterObservation(
        printer_identity=printer.identity,
        printer_state=PrinterState.IDLE.value,
        provider="fake",
        epistemic_status=EpistemicStatus.STALE,
        retrieval_timestamp=datetime.now(UTC) - timedelta(minutes=30),
    )
    obs_provider = FakeObservationProvider(observation)
    discovery = FakeDiscoveryProvider([printer])
    capability = FakeCapabilityProvider({"printer-1": caps})

    service = PrinterService(
        printer_repository=printer_repo,
        discovery_provider=discovery,
        capability_provider=capability,
        observation_provider=obs_provider,
        event_repository=event_repo,
    )

    status = asyncio_await(service.get_status("printer-1"))
    assert status["epistemic_status"] == EpistemicStatus.STALE.value
    assert status["printer_id"] == "printer-1"


def test_assumed_observation_does_not_bypass_validation():
    job_repo = InMemoryPrintJobRepository()
    exec_repo = InMemoryExecutionRepository()
    event_repo = InMemoryEventRepository()

    submission = FakeSubmissionProvider()
    service = PrintJobService(
        job_repository=job_repo,
        execution_repository=exec_repo,
        event_repository=event_repo,
        submission_provider=submission,
    )

    job = PrintJob(
        job_id="job-1",
        source_document="file:///tmp/doc.pdf",
        document_format="pdf",
        resolved_printer="printer-1",
    )
    job = asyncio_await(service.create_job(job))
    assert job.state == PrintJobState.CREATED

    try:
        job = asyncio_await(service.submit_job(job))
    except ValueError:
        pass
    else:
        raise AssertionError("Expected invalid transition to CREATED -> SUBMITTED")

    job = asyncio_await(service.get_job("job-1"))
    assert job.state == PrintJobState.CREATED


def test_epistemic_non_authority_prevents_direct_capability_fabrication():
    event_repo = InMemoryEventRepository()
    printer_repo = InMemoryPrinterRepository()

    caps = PrinterCapabilities(color=True, duplex=False, supported_document_formats=["pdf"])
    printer = Printer(
        printer_id="printer-1",
        name="Fabrication Guard",
        identity="urn:printer:fabrication:1",
        protocol="ipp",
        capabilities=caps,
        state=PrinterState.IDLE,
    )
    asyncio_await(printer_repo.save(printer))

    assumed_observation = PrinterObservation(
        printer_identity=printer.identity,
        printer_state=PrinterState.IDLE.value,
        provider="fake",
        epistemic_status=EpistemicStatus.ASSUMED,
        normalized_data={"color": True, "duplex": True},
    )
    obs_provider = FakeObservationProvider(assumed_observation)
    discovery = FakeDiscoveryProvider([printer])
    capability = FakeCapabilityProvider({"printer-1": caps})

    service = PrinterService(
        printer_repository=printer_repo,
        discovery_provider=discovery,
        capability_provider=capability,
        observation_provider=obs_provider,
        event_repository=event_repo,
    )

    cap_data = asyncio_await(service.get_capabilities("printer-1"))
    assert cap_data["color"] is True
    assert cap_data["duplex"] is False


def test_contradicted_observation_does_not_corrupt_domain_state():
    event_repo = InMemoryEventRepository()
    printer_repo = InMemoryPrinterRepository()

    caps = PrinterCapabilities(color=True, duplex=False, supported_document_formats=["pdf"])
    printer = Printer(
        printer_id="printer-1",
        name="Contradiction",
        identity="urn:printer:contradiction:1",
        protocol="ipp",
        capabilities=caps,
        state=PrinterState.IDLE,
    )
    asyncio_await(printer_repo.save(printer))

    contradicted_observation = PrinterObservation(
        printer_identity=printer.identity,
        printer_state=PrinterState.ERROR.value,
        provider="fake",
        epistemic_status=EpistemicStatus.CONTRADICTED,
        normalized_data={"color": False},
    )
    obs_provider = FakeObservationProvider(contradicted_observation)
    discovery = FakeDiscoveryProvider([printer])
    capability = FakeCapabilityProvider({"printer-1": caps})

    service = PrinterService(
        printer_repository=printer_repo,
        discovery_provider=discovery,
        capability_provider=capability,
        observation_provider=obs_provider,
        event_repository=event_repo,
    )

    status = asyncio_await(service.get_status("printer-1"))
    assert status["epistemic_status"] == EpistemicStatus.CONTRADICTED.value

    retrieved = asyncio_await(printer_repo.get("printer-1"))
    assert retrieved.state == PrinterState.IDLE


def test_observation_timestamp_is_preserved():
    now = datetime.now(UTC)
    obs = PrinterObservation(
        printer_identity="urn:printer:1",
        printer_state=PrinterState.IDLE.value,
        timestamp=now,
    )
    assert obs.timestamp == now
    assert obs.retrieval_timestamp is None


def test_observation_age_is_deterministically_calculable():
    now = datetime.now(UTC)
    obs = PrinterObservation(
        printer_identity="urn:printer:1",
        printer_state=PrinterState.IDLE.value,
        retrieval_timestamp=now - timedelta(seconds=42),
    )
    age = observation_age_seconds(obs, now)
    assert abs(age - 42.0) < 0.1


def test_staleness_does_not_mutate_original_observation():
    now = datetime.now(UTC)
    obs = PrinterObservation(
        printer_identity="urn:printer:1",
        printer_state=PrinterState.IDLE.value,
        epistemic_status=EpistemicStatus.OBSERVED,
        retrieval_timestamp=now - timedelta(seconds=120),
    )
    policy = FreshnessPolicy(stale_max_age_seconds=60)
    qualified = qualify_observation(obs, policy, now)
    assert obs.epistemic_status == EpistemicStatus.OBSERVED
    assert qualified.epistemic_status == EpistemicStatus.STALE


def test_stale_information_cannot_become_current():
    now = datetime.now(UTC)
    obs = PrinterObservation(
        printer_identity="urn:printer:1",
        printer_state=PrinterState.IDLE.value,
        epistemic_status=EpistemicStatus.STALE,
        retrieval_timestamp=now - timedelta(seconds=120),
    )
    policy = FreshnessPolicy(fresh_max_age_seconds=60)
    qualified = qualify_observation(obs, policy, now)
    assert qualified.epistemic_status == EpistemicStatus.STALE


def test_unavailable_observation_remains_unknown():
    now = datetime.now(UTC)
    obs = PrinterObservation(
        printer_identity="urn:printer:1",
        printer_state=PrinterState.UNKNOWN.value,
        epistemic_status=EpistemicStatus.UNKNOWN,
    )
    policy = FreshnessPolicy(stale_max_age_seconds=1)
    qualified = qualify_observation(obs, policy, now)
    assert qualified.epistemic_status == EpistemicStatus.UNKNOWN


def test_provider_specific_freshness_policy():
    now = datetime.now(UTC)
    obs = PrinterObservation(
        printer_identity="urn:printer:1",
        printer_state=PrinterState.IDLE.value,
        provider="provider-a",
        retrieval_timestamp=now - timedelta(seconds=120),
    )
    policy = FreshnessPolicy(provider_id="provider-a", stale_max_age_seconds=60)
    qualified = qualify_observation(obs, policy, now)
    assert qualified.epistemic_status == EpistemicStatus.STALE


def test_accidental_freshness_promotion_is_negative():
    now = datetime.now(UTC)
    obs = PrinterObservation(
        printer_identity="urn:printer:1",
        printer_state=PrinterState.IDLE.value,
        epistemic_status=EpistemicStatus.STALE,
        retrieval_timestamp=now - timedelta(seconds=120),
    )
    policy = FreshnessPolicy(fresh_max_age_seconds=60)
    qualified = qualify_observation(obs, policy, now)
    assert qualified.epistemic_status == EpistemicStatus.STALE
