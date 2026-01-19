from abc import ABC, abstractmethod
from uuid import UUID

from todo_app.domain.entities.project import Project

class ProjectRepository(ABC):

    @abstractmethod
    def get(self, project_id: UUID) -> Project:
        pass

    @abstractmethod
    def save(self, project: Project) -> None:
        pass

    @abstractmethod
    def delete(self, project_id: UUID) -> None:
        pass