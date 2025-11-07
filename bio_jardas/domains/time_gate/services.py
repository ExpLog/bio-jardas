from disnake.ext.commands import Bot

from bio_jardas.domains.time_gate.enums import TimeGateNameEnum
from bio_jardas.domains.time_gate.models import TimeGate
from bio_jardas.domains.time_gate.repositories import TimeGateRepository


class TimeGateService:
    def __init__(
        self,
        bot: Bot,
        gate_repo: TimeGateRepository,
    ):
        self.bot = bot
        self.gate_repo = gate_repo

    async def time_gate(
        self, name: TimeGateNameEnum, snowflake_user_id: int
    ) -> TimeGate:
        return await self.gate_repo.get_or_create(
            name, snowflake_user_id, for_update=True
        )
