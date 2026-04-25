from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box

from scanner.core.base_scanner import Finding, ScanResult, Severity
from scanner.utils.logger import get_logger

logger = get_logger(__name__)

REPORTS_DIR = Path("reports")

_SEVERITY_ORDER: dict[Severity, int] = {
    Severity.CRITICAL: 0,
    Severity.HIGH: 1,
    Severity.MEDIUM: 2,
    Severity.LOW: 3,
    Severity.INFO: 4,
}

_SEVERITY_COLORS: dict[Severity, str] = {
    Severity.CRITICAL: "bold red",
    Severity.HIGH: "red",
    Severity.MEDIUM: "orange",
    Severity.LOW: "yellow",
    Severity.INFO: "white",
}

_console = Console()

class Reporter:
    def __init__(self, results: list[ScanResult]) -> None:
        if results is None:
            logger.warning("No scan results provided to Reporter.")

        self._results = results
        self._scan_time = datetime.now()

    def generate_report(self, save_to_file: bool = True) -> None:
        """ Generate report from scan results. If save to file is true, save report to reports directory. """
        logger.info("Generating report...")
        self._print_summary()
        self._print_findings_table()

        if save_to_file:
            report_content = self._build_report_text()
            self._save_report(report_content)
            logger.info(f"Report saved to file: {REPORTS_DIR}")
        logger.info("Report generation complete.")

    def _print_summary(self) -> None:
        """ Print a high level summary of how many findings exist at each severity level and how many scanners ran. """
        pass # TODO

    def _print_findings_table(self) -> None:
        """ Renders structured rich table of all findings sorted by severity. """
        pass # TODO

    def _collect_findings(self) -> list[Finding]:
        """ Collect all findings from scan results into a combined list. """
        pass # TODO

    def _sort_findings(self, findings: list[Finding]) -> list[Finding]:
        """ Return sorted copy of findings by severity """
        pass # TODO

    def _build_report_text(self) -> str:
        """ 
        Build the plain text version of the report that gets saved to disk.
        Mirrors the terminal output but without rich markup since the file should be readable in any text editor honesly. 
        """
        pass # TODO

    def _save_report(self, content: str) -> Path:
        """ 
        Save the report content to a timestamped file (scan_YYYYMMDD_HHMMSS.txt) in reports directory. 
        Returns the full path to be logged.
        """
        pass # TODO

    def _severity_counts(self) -> dict[Severity, int]:
        """ Count how many findings exist at each severity level. """
        pass # TODO