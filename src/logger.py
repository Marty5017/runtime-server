#!/usr/bin/env python3

"""
General logging file. The built-in python logger or an external service can be
used by just replacing the funcitons in this file
"""

# default modules
import datetime
import traceback

# pylint: disable=fixme
# TODO: these relative paths are non-ideal, change format or logging setup
ALL_LOGS = "../logs/all.log"
ERROR_LOGS = "../logs/error.log"
EXCEPTION_LOGS = "../logs/exception.log"


def log_message(
    level: str,
    timestamp: str,
    message: str,
    file_path: str
) -> None:
    """
    Write message to supplied file path
    """
    entry = f"{level} [{timestamp}]: {message}\n"
    with open(file_path, "a", encoding='utf8') as log:
        log.write(entry)


def get_timestamp() -> str:
    """
    Standardise how date strings are retrieved
    """
    return datetime.datetime.utcnow().isoformat()


def log_info(message: str) -> None:
    """
    General info messages. E.g. Logging all incoming requests
    """
    timestamp = get_timestamp()
    log_message("INFO", timestamp, message, ALL_LOGS)


def log_error(message: str) -> None:
    """
    General error messages. E.g. Invalid API key
    """
    timestamp = get_timestamp()
    log_message("INFO", timestamp, message, ALL_LOGS)
    log_message("ERROR", timestamp, message, ERROR_LOGS)


def log_exception(message: str, exception: Exception) -> None:
    """
    Log all exceptions

    message: the error message to log
    exception: the exception being logged
    """
    err_type = str(type(exception))
    err_text = str(exception.args)
    err_trace = traceback.format_tb(exception.__traceback__)

    entry = (
        f"{message}"
        f"\n\nException type: {err_type}"
        f"\nException text: {err_text}"
        f"\nException traceback: {err_trace}"
    )

    timestamp = get_timestamp()
    log_message("INFO", timestamp, entry, ALL_LOGS)
    log_message("ERROR", timestamp, entry, ERROR_LOGS)
    log_message("EXCEPTION", timestamp, entry, EXCEPTION_LOGS)
