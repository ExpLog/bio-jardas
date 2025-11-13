from dataclasses import dataclass

from bio_jardas.utils import probability_as_percentage


@dataclass(slots=True, frozen=True)
class MessageGroupProbabilities:
    group_name: str
    weight: float
    total_weight: float
    roll: float

    @property
    def weight_percentage(self) -> str:
        return probability_as_percentage(self.weight / self.total_weight)

    @property
    def roll_percentage(self) -> str:
        return probability_as_percentage(self.roll)

    @property
    def percentages(self) -> str:
        return f"w={self.weight_percentage} r={self.roll_percentage}"


@dataclass(slots=True, frozen=True)
class DynamicMessage:
    id: int
    group_id: int
    text: str
