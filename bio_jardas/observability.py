import logging.config
import sys
from collections.abc import Sequence
from typing import Any

import structlog
from structlog.typing import Processor

STRUCTLOG_DEFAULT_PROCESSORS = (
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.CallsiteParameterAdder(
        {
            structlog.processors.CallsiteParameter.FILENAME,
            structlog.processors.CallsiteParameter.LINENO,
        },
    ),
    structlog.processors.TimeStamper(fmt="iso"),
)
THIRD_PARTY_LOGGERS = {
    # add propagate: False to mute
    "disnake.client": {"level": "INFO"},
    "disnake.gateway": {"level": "INFO"},
}


def instrument_logs(
    level: str = "INFO",
    processors: tuple[Processor, ...] | None = None,
    extra_loggers: dict[str, Any] | None = None,
    *,
    force_console_renderer: bool = False,
) -> None:
    processors = processors or STRUCTLOG_DEFAULT_PROCESSORS

    _instrument_stdlib_logs(
        level, processors, extra_loggers, force_console_renderer=force_console_renderer
    )
    _instrument_structlog_logs(processors)


def _instrument_stdlib_logs(
    level: str,
    processors: Sequence[Processor],
    extra_loggers: dict[str, Any],
    *,
    force_console_renderer: bool = False,
) -> None:
    logger_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processors": (
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    (
                        structlog.dev.ConsoleRenderer()
                        if sys.stderr.isatty() or force_console_renderer
                        else structlog.processors.JSONRenderer()
                    ),
                ),
                "foreign_pre_chain": processors,
            },
        },
        "handlers": {
            "default": {
                "level": level,
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "null": {
                "class": "logging.NullHandler",
            },
            "debug_handler": {
                "level": "DEBUG",
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {
                "handlers": ["default"],
                "level": level,
                "propagate": True,
            },
            **extra_loggers,
        },
    }
    logging.config.dictConfig(logger_config)


def _instrument_structlog_logs(processors: Sequence[Processor], /) -> None:
    structlog.configure(
        cache_logger_on_first_use=True,
        context_class=dict,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        processors=[
            structlog.stdlib.filter_by_level,
            *processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
    )
