import sys
import os
import ctypes
import tempfile
from pathlib import Path
from enum import Enum

from scanner.utils.logger import get_logger

logger = get_logger(__name__)


class Platform(Enum):
    MAC = "mac"
    LINUX = "linux"
    WINDOWS = "windows" # ew windows... 


class PlatformDetectionError(RuntimeError):
    """Raised when the current platform cannot be identified or is unsupported."""


class PlatformHelper:
    def __init__(self, platform: Platform | None = None) -> None:
        self._platform = platform if platform is not None else _detect_platform()
        logger.debug("Platform: %s", self._platform.value)

    @property
    def platform(self) -> Platform:
        return self._platform

    def is_mac(self) -> bool:
        return self._platform == Platform.MAC

    def is_linux(self) -> bool:
        return self._platform == Platform.LINUX

    def is_windows(self) -> bool:
        return self._platform == Platform.WINDOWS

    def get_home_dir(self) -> Path:
        return Path.home()

    def get_temp_dir(self) -> Path:
        """Return the system temporary directory."""
        return Path(tempfile.gettempdir())

    def get_ssh_dir(self) -> Path:
        return self.get_home_dir() / ".ssh"

    def get_sensitive_paths(self) -> list[Path]:
        """Return a catalogue of paths that are security-relevant on this platform."""
        if self._platform == Platform.WINDOWS:
            return self._windows_sensitive_paths()
        elif self._platform in (Platform.MAC, Platform.LINUX):
            return self._unix_sensitive_paths()
        else:
            raise PlatformDetectionError(
                f"No sensitive-path catalogue for platform: {self._platform.value}"
            )

    def _windows_sensitive_paths(self) -> list[Path]:
        win_dir = Path(os.environ.get("WINDIR", r"C:\Windows"))
        app_data = Path(
            os.environ.get(
                "APPDATA",
                str(Path.home() / "AppData" / "Roaming"),
            )
        )
        program_files = Path(os.environ.get("PROGRAMFILES", r"C:\Program Files"))
        program_files_x86 = Path(
            os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")
        )
        user_profile = Path(os.environ.get("USERPROFILE", str(self.get_home_dir())))

        return [
            win_dir / "System32",
            app_data,
            program_files,
            program_files_x86,
            user_profile,
            user_profile / ".ssh",
            self.get_temp_dir(),
        ]

    def _unix_sensitive_paths(self) -> list[Path]:
        common = [
            self.get_home_dir(),
            self.get_ssh_dir(),
            Path("/etc/passwd"),
            Path("/etc/shadow"),
            Path("/etc/hosts"),
            Path("/etc/sudoers"),
        ]

        # Log files that exist on both Linux and macOS.
        # Paths that are Linux-only or macOS-only are gated below so callers don't see phantom entries.
        common_logs: list[Path] = []

        if self._platform == Platform.LINUX:
            common_logs = [
                Path("/var/log/auth.log"),   # Debian/Ubuntu
                Path("/var/log/secure"),     # RHEL/CentOS/Fedora
                Path("/var/log/syslog"),     # Debian/Ubuntu
                Path("/var/log/messages"),   # RHEL/CentOS/Fedora
                Path("/var/log/wtmp"),
                Path("/var/log/btmp"),
                Path("/var/log/faillog"),
                Path("/var/log/lastlog"),
                Path("/var/log/utmp"),
            ]
        elif self._platform == Platform.MAC:
            common_logs = [
                Path("/var/log/system.log"),
                Path("/var/log/install.log"),
                Path("/private/var/log/asl"),
                Path("/Library/Logs"),
            ]

        return common + common_logs

    def filter_accessible_paths(
        self,
        paths: list[Path],
        require_read: bool = True,
        include_dirs: bool = True,
    ) -> tuple[list[Path], list[tuple[Path, Exception]]]:
        """Filter *paths* down to those that exist and are accessible."""
        accessible: list[Path] = []
        skipped: list[tuple[Path, Exception]] = []

        for path in paths:
            try:
                if not path.exists():
                    skipped.append((path, FileNotFoundError(f"Does not exist: {path}")))
                    continue

                if path.is_dir():
                    if not include_dirs:
                        skipped.append(
                            (path, ValueError(f"Directories excluded by caller: {path}"))
                        )
                        continue
                    if not os.access(path, os.R_OK | os.X_OK):
                        skipped.append(
                            (path, PermissionError(f"No read+execute access to directory: {path}"))
                        )
                        continue
                else:
                    if require_read and not os.access(path, os.R_OK):
                        skipped.append(
                            (path, PermissionError(f"No read access to file: {path}"))
                        )
                        continue

                accessible.append(path)

            except (OSError, PermissionError) as exc:
                skipped.append((path, exc))

        if skipped:
            logger.debug(
                "%d of %d paths skipped during accessibility check",
                len(skipped),
                len(paths),
            )
            for p, reason in skipped:
                logger.debug("  skipped %s — %s", p, reason)

        return accessible, skipped

    def get_accessible_sensitive_paths(self) -> tuple[list[Path], list[tuple[Path, Exception]]]:
        """Return accessible sensitive paths plus a full audit of what was skipped."""
        return self.filter_accessible_paths(self.get_sensitive_paths())

    def is_root_or_admin(self) -> bool:
        """Return True if the current process has elevated privileges."""
        if self._platform == Platform.WINDOWS:
            return _is_windows_admin()
        elif self._platform in (Platform.MAC, Platform.LINUX):
            return os.geteuid() == 0
        else:
            raise PlatformDetectionError(
                f"Cannot determine privilege level for platform: {self._platform.value}"
            )

def _detect_platform() -> Platform:
    """Detect the current platform from sys.platform."""
    if sys.platform.startswith("darwin"):
        return Platform.MAC
    elif sys.platform.startswith("linux"):
        return Platform.LINUX
    elif sys.platform.startswith("win"):
        return Platform.WINDOWS
    else:
        raise PlatformDetectionError(f"Unsupported platform: {sys.platform!r}")


def _is_windows_admin() -> bool:
    """Return True if the current Windows process has admin privileges."""
    try:
        result = ctypes.windll.shell32.IsUserAnAdmin()
    except AttributeError as exc:
        raise PlatformDetectionError(
            "ctypes.windll is unavailable — are you running on Windows?"
        ) from exc
    except OSError as exc:
        raise PlatformDetectionError(
            f"Win32 IsUserAnAdmin() call failed: {exc}"
        ) from exc

    return result != 0