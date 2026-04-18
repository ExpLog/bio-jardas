from bio_jardas.db.repositories import CRUDRepository
from bio_jardas.domains.config.models import Intensity

__all__ = ["IntensityRepository"]


class IntensityRepository(CRUDRepository[Intensity]):
    model_type = Intensity
