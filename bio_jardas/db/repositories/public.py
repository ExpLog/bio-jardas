from bio_jardas.db import TimeGate
from bio_jardas.db.repositories.base import CRUDRepository


class TimeGateRepository(CRUDRepository[TimeGate]):
    model_type = TimeGate
