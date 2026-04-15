import sys
import os
from pathlib import Path
from enum import Enum

from scanner.utils.logger import get_logger

logger = get_logger(__name__)

class Platform(Enum):
    MAC = "mac"
    LINUX = "linux"
    WINDOWS = "windows" # ew windows... 

class PlatformHelper:
    def __init__(self) -> None:
        self._platform = self.get_platform()
        logger.debug("Detected platform: %s", self._platform.value)

    def get_platform(self) -> Platform:
        if sys.platform.startswith("darwin"):
            return Platform.MAC
        elif sys.platform.startswith("linux"):
            return Platform.LINUX
        elif sys.platform.startswith("win"):
            return Platform.WINDOWS
        else:
            raise RuntimeError(f"Unsupported platform: {sys.platform}")

    def is_mac(self) -> bool:
        return self._platform == Platform.MAC
    
    def is_linux(self) -> bool:
        return self._platform == Platform.LINUX
    
    def is_windows(self) -> bool:
        return self._platform == Platform.WINDOWS

    def get_home_dir(self) -> Path:
        return Path.home()

    def get_temp_dir(self) -> Path:
        pass #TODO: finish this method and add a few more methods after for other directories as well as check if root or admin