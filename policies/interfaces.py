from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from domain.job import PrintJob
from domain.printer import Printer


class PolicyInterface(ABC):
    @abstractmethod
    async def evaluate(self, job: PrintJob, printer: Printer) -> Dict[str, Any]:
        pass
