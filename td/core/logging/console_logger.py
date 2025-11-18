"""td/core/logging/console_logger.py"""
import logging
from logging.handlers import RotatingFileHandler
import os
import sys

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

class ColorFormatter(logging.Formatter):
    """Custom formatter to add colors to log levels in console."""
    COLORS = {
        logging.DEBUG: "\033[94m",     # Blue
        logging.INFO: "\033[92m",      # Green
        logging.WARNING: "\033[93m",   # Yellow
        logging.ERROR: "\033[91m",     # Red
        logging.CRITICAL: "\033[95m"   # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        log_color = self.COLORS.get(record.levelno, "")
        message = super().format(record)
        return f"{log_color}{message}{self.RESET}"


def get_logger(name="TradingApp"):
    """Set up and return a logger with console and file handlers."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # prevent duplicate handlers

    logger.setLevel(logging.DEBUG)

    # -------- Console Handler --------
    console_handler = logging.StreamHandler(sys.stdout)
    console_format = ColorFormatter(
        "[%(asctime)s] %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # -------- Rotating File Handler --------
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "app.log"),
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,
        encoding="utf-8"
    )
    file_format = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    return logger


# The logger your app will use everywhere
log = get_logger()
