from typing import Dict, Sequence
from uuid import UUID

from TodoApp.todo_app.domain.entities.task import Task
from TodoApp.todo_app.domain.entities.project import Project
from TodoApp.todo_app.domain.exceptions import TaskNotFoundError, ProjectNotFoundError
from TodoApp.todo_app.domain.value_objects import TaskStatus
from TodoApp.todo_app.application.repositories.task_repository import TaskRepository
from TodoApp.todo_app.application.repositories.project_repository import ProjectRepository

class InMemoryTaskRepository(TaskRepository):

    def __init__(self):
        self._tasks: Dict[UUID, Task] = {}
    
    def get(self, task_id: UUID) -> Task:
        if Task := self._tasks.get(task_id):
            return task
        raise TaskNotFoundError(task_id)
    
    def save(self, task: Task) -> None:
        self._tasks[task.id] = task

    def delete(self, task_id: UUID) -> None:
        self._tasks.pop(task_id, None)
    
    def find_by_project(self, project_id: UUID) -> Sequence[Task]:
        return [
            task for task in self._tasks.values()
            if task.project_id == project_id
        ]
    
    def get_active_tasks(self) -> Sequence[Task]:
        return [
            task for task in self._tasks.values()
            if task.status != TaskStatus.DONE        
        ]

class InMemoryProjectRepository(ProjectRepository):

    def __init__(self):
 
        self._projects: Dict[UUID, Project] = {}

    def get(self, project_id: UUID) -> Project:

        if project := self._projects.get(project_id):
            return project
        raise ProjectNotFoundError(project_id)

    def save(self, project: Project) -> None:
 
        self._projects[project.id] = project

    def delete(self, project_id: UUID) -> None:

        self._projects.pop(project_id, None)