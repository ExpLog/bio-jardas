import structlog
from dishka import FromDishka
from disnake.ext.commands import Context, command

from bio_jardas.cogs import BaseCog
from bio_jardas.dependency_injection import cog_inject
from bio_jardas.domains.message.services import MessageService
from bio_jardas.domains.time_gate.enums import TimeGateNameEnum
from bio_jardas.domains.time_gate.exceptions import TimeGatedError
from bio_jardas.domains.time_gate.services import TimeGateService

logger = structlog.stdlib.get_logger()


class FortuneTellerCog(BaseCog):
    @command(name="fortune_teller")
    @cog_inject
    async def fortune_teller(
        self,
        context: Context,
        *,
        message_service: FromDishka[MessageService],
        gate_service: FromDishka[TimeGateService],
    ):
        author = context.author
        gate = await gate_service.time_gate(TimeGateNameEnum.FORTUNE_TELLER, author.id)

        try:
            with gate.lock():
                reply = await message_service.random_message_from_group(
                    "fortune_cookie"
                )
                await logger.ainfo(
                    "Told a fortune",
                    message_id=reply.id,
                    resets_at=gate.resets_at.format_iso(),
                )
                await context.channel.send(reply.interpolate_mention(author.mention))
        except TimeGatedError:
            await logger.ainfo(
                "Time-gated a fortune", resets_at=gate.resets_at.format_iso()
            )
            await context.reply("Só tens direito a 1 por semana caralho")
