from bio_jardas.db.repositories import CRUDRepository
from bio_jardas.domains.time_gate.enums import TimeGateNameEnum
from bio_jardas.domains.time_gate.models import TimeGate


class TimeGateRepository(CRUDRepository[TimeGate]):
    model_type = TimeGate

    async def get_or_create(
        self, name: TimeGateNameEnum, user_snowflake_id: int, for_update: bool = False
    ) -> TimeGate:
        time_gate = await self.get_one_or_none(
            TimeGate.name == name,
            TimeGate.user_snowflake_id == user_snowflake_id,
            for_update=for_update,
        )
        if not time_gate:
            time_gate = TimeGate(user_snowflake_id=user_snowflake_id, name=name)
            await self.add(time_gate)
        return time_gate
