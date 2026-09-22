import pytest
from domain.job import PrintJob
from domain.events import PrintJobCreated, PrintJobValidated
from domain.execution import PrintExecution
from simulation.simulator import DeterministicPrinterSimulator
from domain.capabilities import PrinterCapabilities
from domain.printer import Printer, PrinterState


def test_job_provenance_retained():
    provenance = {"source": "api", "user": "alice"}
    job = PrintJob(job_id="j1", source_document="doc.pdf", document_format="pdf", provenance=provenance)
    assert job.provenance == provenance


def test_execution_provenance_retained():
    execution = PrintExecution(
        execution_id="e1",
        job_id="j1",
        printer_id="p1",
        requested_operation="submit",
        provenance={"provider": "sim"},
    )
    assert execution.provenance == {"provider": "sim"}


def test_simulator_observation_provenance():
    sim = DeterministicPrinterSimulator(seed=1)
    caps = PrinterCapabilities(color=True, duplex=False, supported_document_formats=["pdf"], supported_protocols=["ipp"])
    printer = Printer(printer_id="p1", name="P", identity="i", protocol="ipp", capabilities=caps, state=PrinterState.IDLE)
    sim.register_printer(printer)
    import asyncio
    obs = asyncio.run(sim.observe("p1"))
    assert "source" in obs.provenance or obs.source is not None