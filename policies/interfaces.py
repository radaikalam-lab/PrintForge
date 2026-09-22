from abc import ABC, abstractmethod
from typing import Any

from domain.job import PrintJob
from domain.printer import Printer


class PolicyInterface(ABC):
    @abstractmethod
    async def evaluate(self, job: PrintJob, printer: Printer) -> dict[str, Any]:
        pass
