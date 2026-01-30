# ruff: noqa: ARG002
from typing import Any

from sqlalchemy import DateTime, Dialect, TypeDecorator
from sqlalchemy.sql.type_api import _T
from whenever import ZonedDateTime


class ZonedDateTimeType(TypeDecorator):
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: _T | None, dialect: Dialect) -> Any:
        if value is None:
            return None
        if not isinstance(value, ZonedDateTime):
            raise TypeError(f"Expected ZonedDateTime, got {type(value).__name__}")
        return value.py_datetime()

    def process_result_value(self, value: Any | None, dialect: Dialect) -> _T | None:
        if value is None:
            return None
        return ZonedDateTime.from_py_datetime(value)
