from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DeletionOutcome:

    entity_id: UUID

    def __str__(self) -> str:
        return f"Successfully deleted entity with ID: {self.entity_id}"