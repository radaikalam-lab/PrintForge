from datetime import datetime

from domain.capabilities import PrinterCapabilities
from domain.job import PrintJob, PrintJobState
from domain.printer import Printer, PrinterState


def test_print_job_creation():
    job = PrintJob(
        job_id="job-1",
        source_document="file:///tmp/report.pdf",
        document_format="pdf",
    )
    assert job.job_id == "job-1"
    assert job.state == PrintJobState.CREATED
    assert job.copies == 1
    assert job.provenance == {}


def test_print_job_defaults():
    job = PrintJob(
        job_id="job-2",
        source_document="doc.pdf",
        document_format="pdf",
    )
    assert job.duplex is False
    assert job.priority == 0
    assert isinstance(job.submission_time, datetime)


def test_printer_creation():
    caps = PrinterCapabilities(color=True, duplex=True, supported_document_formats=["pdf"])
    printer = Printer(
        printer_id="printer-1",
        name="Test Printer",
        identity="urn:printer:1",
        protocol="ipp",
        capabilities=caps,
        state=PrinterState.IDLE,
    )
    assert printer.printer_id == "printer-1"
    assert printer.state == PrinterState.IDLE
    assert printer.capabilities.color is True
    assert printer.capabilities.duplex is True
