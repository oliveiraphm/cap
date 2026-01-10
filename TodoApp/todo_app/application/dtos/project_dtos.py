from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Sequence, Self
from uuid import UUID

from TodoApp.todo_app.domain.exceptions import BusinessRuleViolation
from TodoApp.todo_app.domain.value_objects import ProjectStatus
from TodoApp.todo_app.application.dtos.task_dtos import TaskResponse
from TodoApp.todo_app.domain.entities.project import Project

@dataclass(frozen=True)
class CreateProjectRequest:

    name: str
    description: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Project name is required")
        if len(self.name) > 100:
            raise ValueError("Project name cannot exceed 100 characters")
        if len(self.description) > 2000:
            raise ValueError("Description cannot exceed 2000 characters")
        
    def to_execution_params(self) -> dict:
        return {
            "name": self.name.strip(),
            "description": self.description.strip(),
        }
    
@dataclass(frozen=True)
class CompleteProjectRequest:

    project_id: str
    completion_notes: Optional[str] = None

    def __post_init__(self) -> None:

        if not self.project_id.strip():
            raise ValueError("Project ID is required")
        if self.completion_notes and len(self.completion_notes) > 1000:
            raise ValueError("Completion notes cannot exceed 1000 characters")
        try:
            UUID(self.project_id)
        except ValueError:
            raise ValueError("Invalid project ID format")

    def to_execution_params(self) -> dict:
        return {
            "project_id": UUID(self.project_id),
            "completion_notes": self.completion_notes,
        } 

@dataclass(frozen=True)
class ProjectResponse:

    id: str
    name: str
    description: str
    status: ProjectStatus
    completion_date: Optional[datetime]
    tasks: Sequence[TaskResponse]

    @classmethod
    def from_entity(cls, project: Project) -> Self:
        return cls(
            id=str(project.id),
            name=project.name,
            description=project.description,
            status=project.status,
            completion_date=project.completed_at if project.completed_at else None,
            tasks=[TaskResponse.from_entity(task) for task in project.tasks],           
        )
    
@dataclass(frozen=True)
class CompleteProjectResponse:

    id: str
    status: ProjectStatus
    completion_date: datetime
    task_count: int
    completion_notes: Optional[str]

    @classmethod
    def from_entity(cls, project: Project) -> Self:
        if project.completed_at is None:
            raise BusinessRuleViolation("Project does not have a completion date")
        return cls(
            id=str(project.id),
            status=project.status,
            completion_date=project.completed_at,
            task_count=len(project.tasks),
            completion_notes=project.completion_notes,
        ) 

@dataclass
class UpdateProjectRequest:

    project_id: str
    name: Optional[str] = None
    description: Optional[str] = None

    def to_execution_params(self) -> dict:

        return {
            "project_id": UUID(self.project_id),
            "name": self.name,
            "description": self.description
        }