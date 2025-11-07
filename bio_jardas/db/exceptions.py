from typing import Any

from bio_jardas.db.models import Base
from bio_jardas.exceptions import JardasError


class DatabaseError(JardasError):
    pass


class EntityNotFoundError(DatabaseError):
    def __init__(self, entity_type: type[Base], entity_identifier: Any):
        self.entity_type = entity_type.__name__
        self.entity_identifier = entity_identifier
        super().__init__(f"{self.entity_type} '{self.entity_identifier}' not found")


class UpsertForbiddenError(DatabaseError):
    pass
