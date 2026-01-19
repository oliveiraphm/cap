from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from todo_app.domain.entities.entity import Entity
from todo_app.domain.entities.task import Task
from todo_app.domain.exceptions import BusinessRuleViolation
from todo_app.domain.value_objects import ProjectType, TaskStatus,  ProjectStatus


@dataclass
class Project(Entity):

    INBOX_NAME = "INBOX"

    name: str
    description: str = ""
    project_type: ProjectType = field(default=ProjectType.REGULAR)
    status: ProjectStatus = field(default=ProjectStatus.ACTIVE, init=False)
    completed_at: Optional[datetime] = field(default=None, init=False)
    completion_notes: Optional[str] = field(default=None, init=False)
    _tasks: dict[UUID, Task] = field(default_factory=dict, init=False)

    @classmethod
    def create_inbox(cls) -> "Project":
        return cls(
            name="INBOX",
            description="Default project for unassigned tasks",
            project_type=ProjectType.INBOX,
        )

    def add_task(self, task: Task) -> None:
        if self.status == ProjectStatus.COMPLETED:
            raise ValueError("Cannot add tasks to a completed project")
        self._tasks[task.id] = task
        task.project_id = self.id

    def get_task(self, task_id: UUID) -> Optional[Task]:

        return self._tasks.get(task_id)

    @property
    def tasks(self) -> list[Task]:
        return list(self._tasks.values())

    @property
    def incomplete_tasks(self) -> list[Task]:
        return [task for task in self.tasks if task.status != TaskStatus.DONE]

    def mark_completed(self, notes: Optional[str] = None) -> None:

        if self.project_type == ProjectType.INBOX:
            raise BusinessRuleViolation("The INBOX project cannot be completed")
        self.status = ProjectStatus.COMPLETED
        self.completed_at = datetime.now()
        self.completion_notes = notes