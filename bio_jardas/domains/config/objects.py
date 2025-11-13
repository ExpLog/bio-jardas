import random
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ReplyIntensityEnum(StrEnum):
    SLEEPING = "sleeping"
    PUNY = "puny"
    MILD = "mild"
    NORMAL = "normal"
    ANNOYING = "annoying"
    INTENSE = "intense"
    EDGELORD = "edgelord"


class ReplyIntensityConfig(BaseModel):
    intensity: ReplyIntensityEnum = ReplyIntensityEnum.NORMAL

    model_config = ConfigDict(extra="ignore")

    def is_sleeping(self) -> bool:
        return self.intensity == ReplyIntensityEnum.SLEEPING

    def reply_probability(self) -> float:
        match self.intensity:
            case ReplyIntensityEnum.SLEEPING:
                probability = 0.0
            case ReplyIntensityEnum.PUNY:
                probability = 1 / 50
            case ReplyIntensityEnum.MILD:
                probability = 1 / 25
            case ReplyIntensityEnum.NORMAL:
                probability = 1 / 17
            case ReplyIntensityEnum.ANNOYING:
                probability = 1 / 13
            case ReplyIntensityEnum.INTENSE:
                probability = 1 / 10
            case ReplyIntensityEnum.EDGELORD:
                probability = 1.0
            case _:
                probability = 1 / 17
        return probability

    def roll_should_reply(self) -> bool:
        return random.random() > self.reply_probability()
