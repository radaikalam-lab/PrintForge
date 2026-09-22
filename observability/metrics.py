from abc import ABC, abstractmethod


class MetricsInterface(ABC):
    @abstractmethod
    def increment(self, metric_name: str, tags: dict[str, str] | None = None) -> None:
        pass

    @abstractmethod
    def gauge(self, metric_name: str, value: float, tags: dict[str, str] | None = None) -> None:
        pass

    @abstractmethod
    def histogram(self, metric_name: str, value: float, tags: dict[str, str] | None = None) -> None:
        pass
