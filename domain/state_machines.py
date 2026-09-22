from domain.job import PrintJobState
from domain.printer import PrinterState

VALID_JOB_TRANSITIONS = {
    PrintJobState.CREATED: [PrintJobState.VALIDATED, PrintJobState.VALIDATION_FAILED, PrintJobState.CANCELLED],
    PrintJobState.VALIDATED: [PrintJobState.QUEUED, PrintJobState.CANCELLED],
    PrintJobState.QUEUED: [PrintJobState.SCHEDULED, PrintJobState.BLOCKED, PrintJobState.CANCELLED],
    PrintJobState.SCHEDULED: [PrintJobState.SUBMITTED, PrintJobState.QUEUED, PrintJobState.CANCELLED],
    PrintJobState.SUBMITTED: [PrintJobState.PROCESSING, PrintJobState.CANCELLED],
    PrintJobState.PROCESSING: [PrintJobState.COMPLETED, PrintJobState.FAILED, PrintJobState.CANCELLED, PrintJobState.BLOCKED],
    PrintJobState.BLOCKED: [PrintJobState.QUEUED, PrintJobState.CANCELLED],
    PrintJobState.COMPLETED: [PrintJobState.ARCHIVED],
    PrintJobState.VALIDATION_FAILED: [PrintJobState.ARCHIVED],
    PrintJobState.CANCELLED: [PrintJobState.ARCHIVED],
    PrintJobState.FAILED: [PrintJobState.ARCHIVED],
    PrintJobState.ARCHIVED: [],
}


def validate_job_transition(current_state: PrintJobState, new_state: PrintJobState) -> None:
    allowed = VALID_JOB_TRANSITIONS.get(current_state, [])
    if new_state not in allowed:
        raise ValueError(
            f"Illegal state transition: {current_state.value} -> {new_state.value}. "
            f"Allowed transitions from {current_state.value}: {[s.value for s in allowed]}"
        )

VALID_PRINTER_TRANSITIONS = {
    PrinterState.IDLE: [PrinterState.PROCESSING, PrinterState.OFFLINE, PrinterState.ERROR],
    PrinterState.PROCESSING: [PrinterState.IDLE, PrinterState.ERROR, PrinterState.OFFLINE],
    PrinterState.ERROR: [PrinterState.IDLE, PrinterState.OFFLINE],
    PrinterState.OFFLINE: [PrinterState.IDLE],
    PrinterState.UNKNOWN: [PrinterState.IDLE, PrinterState.OFFLINE],
}


def validate_printer_transition(current_state: PrinterState, new_state: PrinterState) -> None:
    allowed = VALID_PRINTER_TRANSITIONS.get(current_state, [])
    if new_state not in allowed:
        raise ValueError(
            f"Illegal state transition: {current_state.value} -> {new_state.value}. "
            f"Allowed transitions from {current_state.value}: {[s.value for s in allowed]}"
        )
