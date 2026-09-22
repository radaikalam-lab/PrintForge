import pytest

from domain.job import PrintJobState
from domain.printer import PrinterState
from domain.state_machines import (
    VALID_JOB_TRANSITIONS,
    VALID_PRINTER_TRANSITIONS,
    validate_job_transition,
    validate_printer_transition,
)


def test_valid_job_transitions():
    validate_job_transition(PrintJobState.CREATED, PrintJobState.VALIDATED)


def test_invalid_job_transition():
    with pytest.raises(ValueError):
        validate_job_transition(PrintJobState.CREATED, PrintJobState.COMPLETED)


def test_job_transitions_are_explicit():
    for state, allowed in VALID_JOB_TRANSITIONS.items():
        for target in allowed:
            validate_job_transition(state, target)
        for target in PrintJobState:
            if target not in allowed:
                with pytest.raises(ValueError):
                    validate_job_transition(state, target)


def test_valid_printer_transitions():
    validate_printer_transition(PrinterState.IDLE, PrinterState.PROCESSING)


def test_invalid_printer_transition():
    with pytest.raises(ValueError):
        validate_printer_transition(PrinterState.IDLE, PrinterState.UNKNOWN)


def test_printer_transitions_are_explicit():
    for state, allowed in VALID_PRINTER_TRANSITIONS.items():
        for target in allowed:
            validate_printer_transition(state, target)
        for target in PrinterState:
            if target not in allowed:
                with pytest.raises(ValueError):
                    validate_printer_transition(state, target)
