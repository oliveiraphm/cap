from copy import deepcopy
from dataclasses import dataclass

from TodoApp.todo_app.application.common.result import Result, Error
from TodoApp.todo_app.application.dtos.project_dtos import CreateProjectRequest, ProjectResponse, CompleteProjectRequest, CompleteProjectResponse
from TodoApp.todo_app.application.service_ports.notifications import NotificationPort
from TodoApp.todo_app.application.repositories.project_repository import ProjectRepository
from TodoApp.todo_app.application.repositories.task_repository import TaskRepository
from TodoApp.todo_app.domain.entities.project import Project
from TodoApp.todo_app.domain.exceptions import ValidationError, BusinessRuleViolation, ProjectNotFoundError

@dataclass
class CreateProjectUseCase:
    
    project_repository: ProjectRepository

    def execute(self, request: CreateProjectRequest) -> Result:

        try:
            params = request.to_execution_params()
            project = Project(name=params["name"], description=params["description"])
            self.project_respository.save(project)
            
            return Result.success(ProjectResponse.from_entity(project))
        
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
        

@dataclass
class CompleteProjectUseCase:

    project_repository: ProjectRepository
    task_repository: TaskRepository
    notification_service: NotificationPort

    def execute(self, request: CompleteProjectRequest) -> Result:
        try:
            params = request.to_execution_params()
            project = self.project_repository.get(params["project_id"])

            project_snapshot = deepcopy(project)
            task_snapshots = {task.id: deepcopy(task) for task in project.incomplete_tasks}

            try:
                for task in project.imcomplete_tasks:
                    task.complete()
                    self.task_repository.save(task)

                project.mark_completed(notes=params["completion_notes"],)
                self.project_repository.save(project)
                for task in project_snapshot.incomplete_tasks:
                    self.notification_service.notify_task_completed(task)
                return Result.success(CompleteProjectResponse.from_entity(project))
            except (ValidationError, BusinessRuleViolation) as e:
                for task_id, task_snapshot in task_snapshots.items():
                    self.task_repository.save(task_snapshot)
                self.project_repository.save(project_snapshot)
                raise

        except ProjectNotFoundError:
            return Result.failure(Error.not_found("Project", str(params["project_id"])))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))