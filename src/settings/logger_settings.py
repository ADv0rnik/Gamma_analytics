import json
import logging
import pathlib

from contextlib import suppress


BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent


class ColoredJSONFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[34m",  # Blue
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[41m",  # Red background
        "RESET": "\033[0m"  # Reset to default
    }

    def format(self, record):
        filepath = pathlib.Path(record.pathname)

        with suppress(ValueError):
            filepath = filepath.relative_to(BASE_DIR)

        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
            "time": self.formatTime(record),
            "event_source": record.name,
            "filename": filepath.as_posix(),
            "lineno": record.lineno
        }

        json_log_record = json.dumps(log_record)

        colored_output = f"{self.COLORS.get(record.levelname, self.COLORS["RESET"])}{json_log_record}{self.COLORS["RESET"]}"

        return colored_output
