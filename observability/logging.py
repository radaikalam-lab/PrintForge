import logging
import sys
from typing import Optional
from datetime import datetime, UTC


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


class CorrelationContext:
    def __init__(self, job_id: Optional[str] = None, printer_id: Optional[str] = None, execution_id: Optional[str] = None):
        self.job_id = job_id
        self.printer_id = printer_id
        self.execution_id = execution_id
        self.timestamp = datetime.now(UTC)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "printer_id": self.printer_id,
            "execution_id": self.execution_id,
            "timestamp": self.timestamp.isoformat(),
        }
