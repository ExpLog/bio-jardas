from disnake import Forbidden, Role
from disnake.ext.commands import Context

import bio_jardas.exceptions as exc
from bio_jardas.domains.game.games.base import Game
from bio_jardas.domains.game.objects import GameResult
from bio_jardas.domains.game.services import GameService
from bio_jardas.settings import SETTINGS


class ShadowBanGame(Game):
    name = "shadowban"

    def __init__(self, hours: int, game_service: GameService):
        super().__init__(game_service)
        self.hours = hours

    async def play(self, context: Context) -> GameResult:
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
            await context.channel.send(
                f"{player.mention} is shining brighter than the shadows!"
            )

        await player.add_roles(shadow_role)
        await player.remove_roles(member_role)
        await player.send("You are now shadow banned. Get to work weakling!")

        # TODO: need scheduled tasks to do this properly
        #  we'll need to schedule unbanning the user

    @staticmethod
    def _find_role(role_name: str, roles: list[Role]) -> Role | None:
        return next((role for role in roles if role.name == role_name), None)
