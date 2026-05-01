from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class Severity(Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Finding:
    title: str
    description: str
    severity: Severity
    location: str
    recommendation: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ScanResult:
    scanner_name: str
    findings: list[Finding] = field(default_factory=list)
    completed: bool = False
    error: str | None = None


class BaseScanner(ABC):
    def __init__(self, target: str) -> None:
        self._target = target
        self._result = self._create_result()

    @property
    @abstractmethod
    def name(self) -> str:
        pass #Override

    @abstractmethod
    def run(self) -> ScanResult:
        pass #Override

    def _create_finding(
            self,
            title: str,
            desc: str,
            severity: Severity,
            loc: str,
            recommendation: str
    ) -> Finding:
        return Finding(
            title = title,
            description = desc,
            Severity = severity,
            location = loc,
            recommendation = recommendation
        )

    def _create_result(self) -> ScanResult:
        """By the time a subclass calls super().__init__() the name property is already resolved on the concrete instance."""
        return ScanResult(scanner_name = self.name)