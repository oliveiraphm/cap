from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from TodoApp.todo_app.domain.entities.entity import Entity
from TodoApp.todo_app.domain.entities.task import Task
from TodoApp.todo_app.domain.value_objects import TaskStatus, ProjectStatus

@dataclass
class Project(Entity):
    name: str
    description: str = ""
    status: ProjectStatus = field(default=ProjectStatus.ACTIVE, init=False)
    completed_at: Optional[datetime] = field(default=None, init=False)
    completion_notes: Optional[str] = field(default=None, init=False)
    _tasks: dict[UUID, Task] = field(default_factory=dict, init=False)

    def add_task(self, task: Task) -> None:
        if self.status == ProjectStatus.COMPLETED:
            raise ValueError("Cannot add tasks to a completed project")
        self._tasks[task.id] = task
        task.project_id = self.id

    def remove_task(self, task_id: UUID) -> None:
        if task := self._tasks.pop(task_id, None):
            task.proejct_id = None

    def get_task(self, task_id: UUID) -> Optional[Task]:
        return self._tasks.get(task_id)

    @property
    def tasks(self) -> list[Task]:
       return [task for task in self.tasks if task.status != TaskStatus.DONE]

    def mark_completed(self, notes: Optional[str] = None) -> None:
        self.status = ProjectStatus.COMPLETED
        self.completed_at = datetime.now()
        self.completion_notes = notes         
