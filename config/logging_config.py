import logging
import sys

from config.config import LOG_FILE_PATH

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging():
    LOG_FILE_PATH.parent.mkdir(exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter(LOG_FORMAT)

    if not _has_stream_handler(root_logger):
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.INFO)
        root_logger.addHandler(stream_handler)

    if not _has_log_file_handler(root_logger):
        file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)


def _has_stream_handler(logger):
    return any(
        isinstance(handler, logging.StreamHandler)
        and not isinstance(handler, logging.FileHandler)
        for handler in logger.handlers
    )


def _has_log_file_handler(logger):
    return any(
        isinstance(handler, logging.FileHandler)
        and getattr(handler, "baseFilename", None) == str(LOG_FILE_PATH)
        for handler in logger.handlers
    )
