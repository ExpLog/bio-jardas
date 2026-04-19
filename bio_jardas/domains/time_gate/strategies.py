from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from whenever import Instant, Time

from bio_jardas.domains.time_gate.enums import TimeGateNameEnum

if TYPE_CHECKING:
    from bio_jardas.domains.time_gate.models import TimeGate


class TimeGateStrategy(ABC):
    _registry: dict[TimeGateNameEnum, type["TimeGateStrategy"]] = {}

    def __init_subclass__(cls, name: TimeGateNameEnum | None = None, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if name is not None:
            TimeGateStrategy._registry[name] = cls

    @classmethod
    def get(cls, name: TimeGateNameEnum) -> "TimeGateStrategy":
        subclass = cls._registry.get(name)
        if not subclass:
            raise ValueError(f"No subclass registered for type {name!r}")
        return subclass()

    @abstractmethod
    def lock_gate(self, time_gate: "TimeGate", action_time: Instant) -> "TimeGate":
        raise NotImplementedError


class FortuneTellerTimeGateStrategy(
    TimeGateStrategy, name=TimeGateNameEnum.FORTUNE_TELLER
):
    def lock_gate(self, time_gate: "TimeGate", action_time: Instant) -> "TimeGate":
        # day of week starts at Monday = 1 and goes to Sunday = 7
        action_time_zoned = action_time.to_system_tz()
        date = action_time_zoned.date()
        days_until_monday = (7 - date.day_of_week().value + 1) % 7

        candidate = (
            action_time_zoned.add(days=days_until_monday)
            .replace_time(Time(hour=7))
            .to_instant()
        )
        if candidate <= Instant.now():
            candidate = candidate.add(weeks=1)

        time_gate.resets_at = candidate
        return time_gate
