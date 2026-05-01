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
    Severity.MEDIUM: "dark_orange",
    Severity.LOW: "yellow",
    Severity.INFO: "white",
}

_TABLE_COLUMN_WIDTHS: dict[str, int] = {
    "Severity": 10,
    "Title": 30,
    "Location": 30,
    "Description": 50,
    "Recommendation": 50,
}

_console = Console()

class Reporter:
    def __init__(self, results: list[ScanResult]) -> None:
        if results is None:
            logger.warning("No scan results provided to Reporter.")

        self._results = results if results is not None else []
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
        severity_counts = self._severity_counts()
        _console.print(f"[bold cyan]Scan Report - {self._scan_time.strftime('%Y-%m-%d %H:%M:%S')}[/bold cyan]")
        _console.print(f"Total Scanners Ran: {len(self._results)}")
        _console.print(f"Total number of findings: {len(self._collect_findings())}")
        
        for severity in _SEVERITY_ORDER:
            count = severity_counts.get(severity, 0)
            color = _SEVERITY_COLORS.get(severity, "white")
            _console.print(f"[{color}]{severity.value}: {count}[/{color}]")

    def _print_findings_table(self) -> None:
        """ Renders structured rich table of all findings sorted by severity. """
        sorted_findings = self._sort_findings(self._collect_findings())
        if not sorted_findings:
            _console.print("[bold green]No findings detected![/bold green]")
            return

        table = Table(title = "Scan Findings", box = box.SIMPLE_HEAVY)

        for column_name, width in _TABLE_COLUMN_WIDTHS.items():
            table.add_column(column_name, style = "bold", width = width, overflow = "fold")

        for finding in sorted_findings:
            severity_color = _SEVERITY_COLORS.get(finding.severity, "white")
            table.add_row(
                f"[{severity_color}]{finding.severity.value}[/{severity_color}]",
                finding.title,
                finding.location,
                finding.description,
                finding.recommendation
            )
        _console.print(table)

    def _collect_findings(self) -> list[Finding]:
        """ Collect all findings from scan results into a combined list. """
        findings = list[Finding] = []
        for result in self._results:
            if result.findings:
                findings.extend(result.findings)
        return findings

    def _sort_findings(self, findings: list[Finding]) -> list[Finding]:
        """ Return sorted copy of findings by severity """
        return sorted(findings, key = lambda f: _SEVERITY_ORDER.get(f.severity, 999))

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