from fastapi import HTTPException
from typing import Optional


class PrintForgeError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details: Optional[dict] = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


def map_to_http(error: PrintForgeError) -> HTTPException:
    return HTTPException(
        status_code=error.status_code,
        detail={
            "code": error.code,
            "message": error.message,
            "details": error.details,
        },
    )


# Deterministic error codes

class InvalidRequestError(PrintForgeError):
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__("INVALID_REQUEST", message, status_code=400, details=details)


class PrinterNotFoundError(PrintForgeError):
    def __init__(self, printer_id: str):
        super().__init__("PRINTER_NOT_FOUND", f"Printer '{printer_id}' not found", status_code=404, details={"printer_id": printer_id})


class JobNotFoundError(PrintForgeError):
    def __init__(self, job_id: str):
        super().__init__("JOB_NOT_FOUND", f"Job '{job_id}' not found", status_code=404, details={"job_id": job_id})


class InvalidStateTransitionError(PrintForgeError):
    def __init__(self, current: str, target: str):
        super().__init__(
            "INVALID_STATE_TRANSITION",
            f"Illegal state transition: {current} -> {target}",
            status_code=409,
            details={"current_state": current, "target_state": target},
        )


class UnsupportedCapabilityError(PrintForgeError):
    def __init__(self, capability: str):
        super().__init__("UNSUPPORTED_CAPABILITY", f"Capability '{capability}' is not supported", status_code=422, details={"capability": capability})


class ProviderFailureError(PrintForgeError):
    def __init__(self, provider: str, operation: str, reason: str):
        super().__init__(
            "PROVIDER_FAILURE",
            f"Provider '{provider}' failed during '{operation}': {reason}",
            status_code=502,
            details={"provider": provider, "operation": operation, "reason": reason},
        )


class PolicyRejectionError(PrintForgeError):
    def __init__(self, policy: str, reason: str):
        super().__init__("POLICY_REJECTION", f"Policy '{policy}' rejected request: {reason}", status_code=403, details={"policy": policy, "reason": reason})


class PersistenceError(PrintForgeError):
    def __init__(self, message: str):
        super().__init__("PERSISTENCE_FAILURE", message, status_code=500)
