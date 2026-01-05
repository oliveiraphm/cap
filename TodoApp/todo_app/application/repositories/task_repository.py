from abc import ABC, abstractmethod
from typing import Sequence
from uuid import UUID

from TodoApp.todo_app.domain.entities.task import Task

class TaskRepository(ABC):

    @abstractmethod
    def get(self, task_id: UUID) -> Task:
        pass

    @abstractmethod
    def save(self, task: Task) -> None:
        pass

    @abstractmethod
    def delete(self, task_id: UUID) -> None:
        pass

    @abstractmethod
    def find_by_project(self, project_id: UUID) -> Sequence[Task]:
        pass

    @abstractmethod
    def get_active_tasks(self) -> Sequence[Task]:
        pass