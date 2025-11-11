from typing import TYPE_CHECKING

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from disnake import Forbidden
from disnake.ext.commands import Context
from structlog.contextvars import get_merged_contextvars
from whenever import ZonedDateTime

import bio_jardas.exceptions as exc
from bio_jardas.domains.game.games.base import Game
from bio_jardas.domains.game.jobs import (
    REMOVE_SHADOW_BAN_JOB_PREFIX,
    remove_shadow_ban,
)
from bio_jardas.domains.game.services import GameService
from bio_jardas.settings import SETTINGS

if TYPE_CHECKING:
    from disnake import Role

logger = structlog.stdlib.get_logger()


class ShadowBanGame(Game[None]):
    name = "shadowban"

    def __init__(
        self, hours: int, game_service: GameService, scheduler: AsyncIOScheduler
    ):
        super().__init__(game_service)
        self.hours = hours
        self.scheduler = scheduler

    async def play(self, context: Context) -> None:
        player = context.author
        guild_roles = context.guild.roles
        shadow_role = self._find_role(SETTINGS.game.shadow_ban_role, guild_roles)
        member_role = self._find_role(SETTINGS.game.member_role, guild_roles)

        try:
            await player.timeout(duration=self.hours * 60 * 60, reason="Shadow Ban")
        except Forbidden as e:
            match e.code:
                case exc.MISSING_PERMISSION_CODE:
                    await context.channel.send(
                        f"{player.mention} is shining brighter than the shadows!"
                    )
                case _:
                    await context.channel.send(
                        f"Error timing out {player.mention}: {e}"
                    )
            await logger.awarning(
                "Role prevented user from being shadow banned", error=str(e)
            )
            return

        await logger.ainfo("Initiating shadow ban")
        await context.channel.send(f"{player.mention} bye bye")
        await player.add_roles(shadow_role)
        await player.remove_roles(member_role)
        await player.send("You are now shadow banned. Get to work weakling!")
        await logger.ainfo("User shadow banned")

        unban_time = ZonedDateTime.now_in_system_tz().add(hours=self.hours)
        self.scheduler.add_job(
            remove_shadow_ban,
            trigger=DateTrigger(run_date=unban_time.py_datetime()),
            args=(
                player.id,
                context.guild.id,
                shadow_role.id,
                member_role.id,
                get_merged_contextvars(logger),
            ),
            id=f"{REMOVE_SHADOW_BAN_JOB_PREFIX}:{context.guild.id}:{player.id}",
            misfire_grace_time=None,
            replace_existing=True,
        )
        return

    @staticmethod
    def _find_role(role_name: str, roles: list["Role"]) -> "Role | None":
        return next((role for role in roles if role.name == role_name), None)
