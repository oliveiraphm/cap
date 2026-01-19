from typing import Dict, Optional, Sequence
from uuid import UUID
from logging import getLogger

from todo_app.domain.entities.project import Project
from todo_app.application.repositories.task_repository import TaskRepository
from todo_app.domain.entities.task import Task
from todo_app.domain.value_objects import TaskStatus, ProjectType
from todo_app.application.repositories.project_repository import ProjectRepository
from todo_app.domain.exceptions import InboxNotFoundError, ProjectNotFoundError, TaskNotFoundError

logger = getLogger(__name__)


class InMemoryTaskRepository(TaskRepository):

    def __init__(self) -> None:
        self._tasks: Dict[UUID, Task] = {}

    def get(self, task_id: UUID) -> Task:

        if task := self._tasks.get(task_id):
            return task
        raise TaskNotFoundError(task_id)

    def save(self, task: Task) -> None:

        logger.debug(f"Saving task {task.id} for project {task.project_id}")
        self._tasks[task.id] = task

    def delete(self, task_id: UUID) -> None:

        self._tasks.pop(task_id, None)

    def find_by_project(self, project_id: UUID) -> Sequence[Task]:

        return [task for task in self._tasks.values() if task.project_id == project_id]

    def get_active_tasks(self) -> Sequence[Task]:

        return [task for task in self._tasks.values() if task.status != TaskStatus.DONE]


class InMemoryProjectRepository(ProjectRepository):

    def __init__(self) -> None:
        self._projects: Dict[UUID, Project] = {}
        self._task_repo: Optional[TaskRepository] = None
        self._initialize_inbox()

    def _initialize_inbox(self) -> None:

        inbox = self._fetch_inbox()
        if not inbox:
            inbox = Project.create_inbox()
            self.save(inbox)

    def _fetch_inbox(self) -> Optional[Project]:

        return next(
            (p for p in self._projects.values() if p.project_type == ProjectType.INBOX), None
        )

    def set_task_repository(self, task_repo: TaskRepository) -> None:

        self._task_repo = task_repo

    def _load_project_tasks(self, project: Project) -> None:

        if not self._task_repo:
            return

        project._tasks.clear()
        for task in self._task_repo.find_by_project(project.id):
            project._tasks[task.id] = task

    def get(self, project_id: UUID) -> Project:

        if project := self._projects.get(project_id):
            self._load_project_tasks(project)
            return project
        raise ProjectNotFoundError(project_id)

    def get_all(self) -> list[Project]:

        projects = list(self._projects.values())
        for project in projects:
            self._load_project_tasks(project)
        return projects

    def save(self, project: Project) -> None:

        self._projects[project.id] = project

    def delete(self, project_id: UUID) -> None:

        self._projects.pop(project_id, None)

    def get_inbox(self) -> Project:

        inbox = self._fetch_inbox()
        if not inbox:
            raise InboxNotFoundError("The Inbox project was not found")
        return inbox