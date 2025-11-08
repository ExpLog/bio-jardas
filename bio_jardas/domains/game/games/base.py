from abc import ABC, abstractmethod

from disnake.ext.commands import Context

from bio_jardas.domains.game.services import GameService


class Game[ResultType](ABC):
    name: str

    def __init__(self, game_service: GameService):
        self.game_service = game_service

    @abstractmethod
    async def play(self, context: Context) -> ResultType:
        raise NotImplementedError
