import pytest

from domain.execution import ExecutionState, PrintExecution
from domain.job import PrintJob, PrintJobState
from domain.state_machines import (
    validate_job_transition,
)


def test_failed_is_terminal_no_retry_to_queued():
    with pytest.raises(ValueError):
        validate_job_transition(PrintJobState.FAILED, PrintJobState.QUEUED)


def test_blocked_transitions():
    validate_job_transition(PrintJobState.QUEUED, PrintJobState.BLOCKED)
    validate_job_transition(PrintJobState.BLOCKED, PrintJobState.QUEUED)
    validate_job_transition(PrintJobState.BLOCKED, PrintJobState.CANCELLED)
    with pytest.raises(ValueError):
        validate_job_transition(PrintJobState.BLOCKED, PrintJobState.COMPLETED)


def test_archived_is_terminal_from_all_terminal_states():
    terminal_states = [
        PrintJobState.COMPLETED,
        PrintJobState.VALIDATION_FAILED,
        PrintJobState.CANCELLED,
        PrintJobState.FAILED,
    ]
    for state in terminal_states:
        validate_job_transition(state, PrintJobState.ARCHIVED)


def test_archived_is_terminal_no_exit():
    with pytest.raises(ValueError):
        validate_job_transition(PrintJobState.ARCHIVED, PrintJobState.QUEUED)


def test_processing_to_blocked_on_provider_unreachable():
    validate_job_transition(PrintJobState.PROCESSING, PrintJobState.BLOCKED)


def test_execution_attempt_states():
    assert ExecutionState.SUBMITTED is not None
    assert ExecutionState.PROCESSING is not None
    assert ExecutionState.COMPLETED is not None
    assert ExecutionState.FAILED is not None
    assert ExecutionState.CANCELLED is not None
    assert ExecutionState.REJECTED is not None
    assert ExecutionState.UNKNOWN is not None


def test_execution_attempt_unknown_represents_uncertainty():
    execution = PrintExecution(
        execution_id="exec-1",
        job_id="job-1",
        printer_id="printer-1",
        provider="fake",
        requested_operation="submit",
        execution_state=ExecutionState.UNKNOWN,
        provenance={"reason": "provider_timeout"},
    )
    assert execution.execution_state == ExecutionState.UNKNOWN
    assert execution.provenance["reason"] == "provider_timeout"


def test_print_job_does_not_use_unknown_state():
    state_values = [member.value for member in PrintJobState]
    assert "UNKNOWN" not in state_values


def test_retry_creates_new_execution_attempt_not_state_rollback():
    job = PrintJob(
        job_id="job-1",
        source_document="doc.pdf",
        document_format="pdf",
        state=PrintJobState.FAILED,
    )
    assert job.state == PrintJobState.FAILED
    with pytest.raises(ValueError):
        validate_job_transition(PrintJobState.FAILED, PrintJobState.QUEUED)


def test_scheduled_to_queued_rescheduling():
    validate_job_transition(PrintJobState.SCHEDULED, PrintJobState.QUEUED)


def test_execution_attempt_rejected_represents_provider_rejection():
    execution = PrintExecution(
        execution_id="exec-1",
        job_id="job-1",
        printer_id="printer-1",
        provider="fake",
        requested_operation="submit",
        execution_state=ExecutionState.REJECTED,
        provenance={"reason": "provider_rejected_job"},
    )
    assert execution.execution_state == ExecutionState.REJECTED
    assert execution.provenance["reason"] == "provider_rejected_job"


def test_print_job_does_not_use_rejected_state():
    state_values = [member.value for member in PrintJobState]
    assert "REJECTED" not in state_values


def test_no_capable_printer_blocks_rather_than_fails():
    validate_job_transition(PrintJobState.QUEUED, PrintJobState.BLOCKED)
    validate_job_transition(PrintJobState.BLOCKED, PrintJobState.QUEUED)
