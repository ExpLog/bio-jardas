# ruff: noqa: ARG002
from enum import StrEnum
from typing import Any

from sqlalchemy import DateTime, Dialect, String, TypeDecorator
from sqlalchemy.sql.type_api import _T
from whenever import ZonedDateTime


# TODO: switch Mapped[datetime] to Mapped[ZonedDateTimeType]
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


class EnumString(TypeDecorator):
    impl = String
    cache_ok = True

    def __init__(self, enum_cls: type[StrEnum], length: int | None = None, **kwargs):
        super().__init__(length=length, **kwargs)
        self.enum_cls = enum_cls

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        try:
            return self.enum_cls(value).value
        except ValueError as exc:
            raise ValueError(
                f"{value!r} is not a valid {self.enum_cls.__name__}"
            ) from exc

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.enum_cls(value)
