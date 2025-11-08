from typing import TYPE_CHECKING

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from disnake import Forbidden
from disnake.ext.commands import Context
from whenever import ZonedDateTime

import bio_jardas.exceptions as exc
from bio_jardas.domains.game.games.base import Game
from bio_jardas.domains.game.services import GameService
from bio_jardas.observability import restore_context_to_logs
from bio_jardas.settings import SETTINGS

if TYPE_CHECKING:
    from disnake import Member, Role, User

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

        await context.channel.send(f"{player.mention} bye bye")
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
            await logger.ainfo("Role prevented user from being shadow banned")
            return

        await logger.ainfo("Initiating shadow ban")
        await player.add_roles(shadow_role)
        await player.remove_roles(member_role)
        await player.send("You are now shadow banned. Get to work weakling!")
        await logger.ainfo("User shadow banned")

        unban_time = ZonedDateTime.now_in_system_tz().add(hours=self.hours)
        self.scheduler.add_job(
            self._remove_shadow_ban,
            trigger=DateTrigger(run_date=unban_time.py_datetime()),
            args=(player, shadow_role, member_role, structlog.get_context(logger)),
        )
        return

    @staticmethod
    def _find_role(role_name: str, roles: list["Role"]) -> "Role | None":
        return next((role for role in roles if role.name == role_name), None)

    @staticmethod
    async def _remove_shadow_ban(
        player: "User | Member",
        shadow_role: "Role",
        member_role: "Role",
        logger_context: dict,
    ) -> None:
        restore_context_to_logs(logger_context)
        await logger.ainfo("Initiating shadow ban reversal")
        await player.add_roles(member_role)
        await player.remove_roles(shadow_role)
        await player.send("Your punishment has ended weakling!")
        await logger.ainfo("User shadow ban reversed")
