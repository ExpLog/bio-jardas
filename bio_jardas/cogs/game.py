import structlog
from dishka import FromDishka
from disnake.ext.commands import Context, command

from bio_jardas.cogs.base import BaseCog
from bio_jardas.dependency_injection import cog_inject
from bio_jardas.domain_objects.game import GameName
from bio_jardas.services.game import GameService
from bio_jardas.shortcuts import author_id

logger = structlog.stdlib.get_logger()


class GameCog(BaseCog):
    @command(name="win")
    @cog_inject
    async def win_game(
        self, context: Context, name: str, *, game_service: FromDishka[GameService]
    ) -> None:
        score = await game_service.increase_score_by(author_id(context), name)
        await logger.ainfo(
            "Score updated",
            score_name=score.name,
            current_score=score.current,
            high_score=score.highest,
        )
        await context.reply("You won!")

    @command(name="highscores")
    @cog_inject
    async def highscores(
        self, context: Context, *, game_service: FromDishka[GameService]
    ) -> None:
        leaderboards = await game_service.leaderboard(
            [
                GameName.RUSSIAN_ROULETTE,
                GameName.HARDCORE_ROULETTE,
                GameName.GLOCK_ROULETTE,
            ]
        )
        leaderboard_displays = [lb.build_display() for lb in leaderboards]
        message = "\n\n".join(leaderboard_displays)
        await context.send(message)
