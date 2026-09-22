import pytest
import asyncio
from simulation.simulator import DeterministicPrinterSimulator
from domain.job import PrintJob, PrintJobState
from domain.printer import Printer, PrinterState
from domain.capabilities import PrinterCapabilities
from domain.state_machines import validate_job_transition


@pytest.fixture
def simulator():
    return DeterministicPrinterSimulator(seed=42)


@pytest.fixture
def sample_printer():
    caps = PrinterCapabilities(
        color=True,
        duplex=True,
        supported_document_formats=["pdf"],
        supported_protocols=["ipp"],
    )
    return Printer(
        printer_id="printer-1",
        name="Sim Printer",
        identity="urn:printer:sim:1",
        protocol="ipp",
        capabilities=caps,
        state=PrinterState.IDLE,
    )


def test_simulator_determinism(simulator, sample_printer):
    simulator.register_printer(sample_printer)
    result1 = asyncio.run(simulator.discover())
    result2 = asyncio.run(simulator.discover())
    assert len(result1) == len(result2)
    assert result1[0].printer_id == result2[0].printer_id


def test_simulator_job_submission(simulator, sample_printer):
    simulator.register_printer(sample_printer)
    job = PrintJob(
        job_id="job-1",
        source_document="file:///tmp/doc.pdf",
        document_format="pdf",
        resolved_printer="printer-1",
    )
    job.state = PrintJobState.SCHEDULED
    execution = asyncio.run(simulator.submit(job))
    assert execution.accepted is True
    assert execution.job_id == "job-1"
    assert job.state == PrintJobState.SUBMITTED


def test_simulator_cancel(simulator, sample_printer):
    simulator.register_printer(sample_printer)
    job = PrintJob(
        job_id="job-1",
        source_document="file:///tmp/doc.pdf",
        document_format="pdf",
        resolved_printer="printer-1",
    )
    job.state = PrintJobState.SCHEDULED
    asyncio.run(simulator.submit(job))
    result = asyncio.run(simulator.cancel("job-1"))
    assert result is True
    assert job.state == PrintJobState.CANCELLED


def test_simulator_advance_to_completed(simulator, sample_printer):
    simulator.register_printer(sample_printer)
    job = PrintJob(
        job_id="job-1",
        source_document="file:///tmp/doc.pdf",
        document_format="pdf",
        resolved_printer="printer-1",
    )
    job.state = PrintJobState.SCHEDULED
    asyncio.run(simulator.submit(job))
    updated = asyncio.run(simulator.advance_job("job-1", PrintJobState.PROCESSING))
    assert updated.state == PrintJobState.PROCESSING
    updated = asyncio.run(simulator.advance_job("job-1", PrintJobState.COMPLETED))
    assert updated.state == PrintJobState.COMPLETED
    assert sample_printer.state == PrinterState.IDLE


def test_simulator_failure_injection(simulator, sample_printer):
    simulator.register_printer(sample_printer)
    job = PrintJob(
        job_id="job-1",
        source_document="file:///tmp/doc.pdf",
        document_format="pdf",
        resolved_printer="printer-1",
    )
    job.state = PrintJobState.SCHEDULED
    asyncio.run(simulator.submit(job))
    updated = asyncio.run(simulator.advance_job("job-1", PrintJobState.PROCESSING))
    assert updated.state == PrintJobState.PROCESSING
    updated = asyncio.run(simulator.advance_job("job-1", PrintJobState.FAILED))
    assert updated.state == PrintJobState.FAILED
    assert sample_printer.state == PrinterState.ERROR
