import logging
import os
import sys

from logging.handlers import RotatingFileHandler

from app.core.config import settings


LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)


def setup_logging():
    """
    Configure application logging.
    """

    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)

    formatter = logging.Formatter(LOG_FORMAT)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    os.makedirs("logs", exist_ok=True)
    file_handler = RotatingFileHandler(
        "logs/application.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logging()


def get_logger(name: str):
    """
    Returns module specific logger.
    """
    return logging.getLogger(name)
