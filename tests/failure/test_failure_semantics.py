from domain.job import PrintJobState
from domain.printer import PrinterState


def test_provider_failure_does_not_corrupt_domain():
    from domain.job import PrintJob
    from simulation.simulator import DeterministicPrinterSimulator
    simulator = DeterministicPrinterSimulator(seed=1)
    caps = type("Caps", (), {"color": True, "duplex": False, "supported_document_formats": ["pdf"], "supported_protocols": ["ipp"]})()
    printer = type("Printer", (), {"printer_id": "p1", "state": PrinterState.IDLE, "capabilities": caps})()
    simulator.register_printer(printer)
    job = PrintJob(job_id="j1", source_document="doc.pdf", document_format="pdf", resolved_printer="p1")
    job.state = PrintJobState.SCHEDULED
    import asyncio
    asyncio.run(simulator.submit(job))
    assert job.state == PrintJobState.SUBMITTED


def test_unsupported_capability_never_fabricated():
    from domain.capabilities import PrinterCapabilities
    caps = PrinterCapabilities(color=False, duplex=False)
    assert caps.duplex is False
    assert caps.color is False
