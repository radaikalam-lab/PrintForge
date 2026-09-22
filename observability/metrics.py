from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class MetricsInterface(ABC):
    @abstractmethod
    def increment(self, metric_name: str, tags: Optional[Dict[str, str]] = None) -> None:
        pass

    @abstractmethod
    def gauge(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        pass

    @abstractmethod
    def histogram(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        pass
