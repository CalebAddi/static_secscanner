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
    Severity: Severity
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
        self.target = target

    @property
    @abstractmethod
    def name(self) -> str:
        pass #TODO

    @abstractmethod
    def run(self) -> ScanResult:
        pass #TODO

    def _create_finding(
            self,
            title: str,
            desc: str,
            severity: Severity,
            location: str,
            recommendation: str
    ) -> Finding:
        pass #TODO

    def _create_result(self) -> ScanResult:
        pass #TODO