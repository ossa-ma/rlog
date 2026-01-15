from contextvars import ContextVar
import logging

# Primarily for logging Context
request_id: ContextVar[str | None] = ContextVar("request_id", default=None)


class ContextFormatter(logging.Formatter):
    """Custom formatter to inject request_id context."""

    def format(self, record: logging.LogRecord):
        if req_id := request_id.get():
            record.request_id = req_id
        else:
            record.request_id = "-"
        return super().format(record)


def setup_logging():
    """Setup structured logging."""
    logger = logging.getLogger()

    handler = logging.StreamHandler()
    # Standard readable format with request_id
    formatter = ContextFormatter(
        fmt="%(asctime)s | %(levelname)-8s | [%(request_id)s] %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    logger.addHandler(handler)

    # Set root level
    logger.setLevel(logging.INFO)

    # Ensure Uvicorn loggers use our handler
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        log = logging.getLogger(logger_name)
        log.handlers = []
        log.addHandler(handler)
        log.propagate = False
