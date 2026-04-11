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
        pass #TODO: finish the setup of PlatformHelper
