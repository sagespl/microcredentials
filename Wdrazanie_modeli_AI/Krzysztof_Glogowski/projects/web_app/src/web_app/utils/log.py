import logging
import sys

from web_app.service.middleware.correlation import CORRELATION_ID


class CorrelationIdFilter(logging.Filter):
    """Logging filter to attach correlation IDs to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = CORRELATION_ID.get()
        return True


def setup_logging_with_correlation_id() -> None:
    """Configures logging and include formatters with correlation id"""
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    sys_stdout_handler = logging.StreamHandler(sys.stdout)
    sys_stdout_handler.setLevel(logging.DEBUG)
    sys_stdout_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - [%(correlation_id)s] - %(message)s"
    )
    correlation_id_filter = CorrelationIdFilter()
    sys_stdout_handler.setFormatter(sys_stdout_formatter)
    sys_stdout_handler.addFilter(correlation_id_filter)
    root.addHandler(sys_stdout_handler)
