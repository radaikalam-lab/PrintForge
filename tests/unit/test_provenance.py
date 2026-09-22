import pytest
from domain.job import PrintJob
from domain.events import PrintJobCreated


def test_provenance_preserved_on_job_creation():
    provenance = {"source": "api", "user": "alice"}
    job = PrintJob(
        job_id="job-1",
        source_document="file:///tmp/doc.pdf",
        document_format="pdf",
        provenance=provenance,
    )
    assert job.provenance == provenance


def test_event_provenance_preserved():
    event = PrintJobCreated(
        job_id="job-1",
        requested_by="alice",
        document_format="pdf",
        provenance={"source": "api"},
    )
    assert event.provenance == {"source": "api"}
    assert event.job_id == "job-1"
