import logging
import sys
from pathlib import Path


LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "scanner.log"

_LOG_FORMAT  = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    LOG_DIR.mkdir(parents = True, exist_ok = True)

    formatter = logging.Formatter(_LOG_FORMAT, _DATE_FORMAT)
    file_handler = logging.FileHandler(LOG_FILE, encoding = "utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.hasHandlers():
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)