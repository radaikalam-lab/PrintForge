import pytest
from simulation.simulator import DeterministicPrinterSimulator
from domain.job import PrintJob, PrintJobState
from domain.printer import Printer, PrinterState
from domain.capabilities import PrinterCapabilities


def test_simulator_deterministic_replay():
    sim1 = DeterministicPrinterSimulator(seed=99)
    sim2 = DeterministicPrinterSimulator(seed=99)
    caps = PrinterCapabilities(color=True, duplex=False, supported_document_formats=["pdf"], supported_protocols=["ipp"])
    p1 = Printer(printer_id="p1", name="P", identity="i", protocol="ipp", capabilities=caps, state=PrinterState.IDLE)
    p2 = Printer(printer_id="p1", name="P", identity="i", protocol="ipp", capabilities=caps, state=PrinterState.IDLE)
    sim1.register_printer(p1)
    sim2.register_printer(p2)
    import asyncio
    r1 = asyncio.run(sim1.discover())
    r2 = asyncio.run(sim2.discover())
    assert r1[0].printer_id == r2[0].printer_id


def test_no_randomness_in_domain_state_machine():
    from domain.state_machines import validate_job_transition
    for _ in range(100):
        validate_job_transition(PrintJobState.CREATED, PrintJobState.VALIDATED)