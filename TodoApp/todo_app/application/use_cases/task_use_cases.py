from copy import deepcopy
from dataclasses import dataclass
from uuid import UUID

from todo_app.application.dtos.operations import DeletionOutcome
from todo_app.application.common.result import Result, Error
from todo_app.application.dtos.task_dtos import CompleteTaskRequest,CreateTaskRequest,TaskResponse,SetTaskPriorityRequest, UpdateTaskRequest
from todo_app.application.service_ports.notifications import NotificationPort
from todo_app.application.repositories.project_repository import ProjectRepository
from todo_app.application.repositories.task_repository import TaskRepository
from todo_app.domain.entities.task import Task
from todo_app.domain.exceptions import TaskNotFoundError, ProjectNotFoundError, ValidationError, BusinessRuleViolation
from todo_app.domain.value_objects import Priority

@dataclass
class CompleteTaskUseCase:
    
    task_repository: TaskRepository
    notification_service: NotificationPort
    
    def execute(self, request: CompleteTaskRequest) -> Result:

        try:
            params = request.to_execution_params()
            task = self.task_repository.get(params["task_id"])

            task_snapshot = deepcopy(task)

            try: 
                task.complete(notes=params["completion_notes"])
                self.task_repository.save(task)
                self.notification_service.notify_task_completed(task)
                
                return Result.success(TaskResponse.from_entity(task))
            
            except (ValidationError, BusinessRuleViolation) as e:
                self.task_repository.save(task_snapshot)
                raise
        
        except TaskNotFoundError:
            return Result.failure(Error.not_found("Task", str(params["task_id"])))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
        
@dataclass
class CreateTaskUseCase:
    task_repository: TaskRepository
    project_repository: ProjectRepository

    def execute(self, request: CreateTaskRequest) -> Result:
        
        try:
            params = request.to_execution_params()
            project_id = params.get("project_id")
            if project_id:
                self.project_repository.get(project_id)
            
            task = Task(
                title=params["title"],
                description=params["description"],
                due_date=params.get("deadline"),
                priority=params.get("priority", Priority.MEDIUM),                
            )
            
            if project_id:
                task.project_id = project_id

            self.task_repository.save(task)

            return Result.success(TaskResponse.from_entity(task))
        except ProjectNotFoundError:
            return Result.failure(Error.not_found("Project", str(params.get("project_id"))))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
        
@dataclass
class SetTaskPriorityUseCase:
    task_repository: TaskRepository
    notification_service: NotificationPort

    def execute(self, request: SetTaskPriorityRequest) -> Result:
        try:
            params = request.to_execution_params()

            task = self.task_repository.get(params["task_id"])
            task.priority = params["priority"]

            self.task_repository.save(task)

            if task.priority == Priority.HIGH:
                self.notification_service.notify_task_high_priority(task)

            return Result.success(TaskResponse.from_entity(task))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))

@dataclass
class GetTaskUseCase:

    task_repository: TaskRepository

    def execute(self, task_id: UUID) -> Result[TaskResponse]:

        try:
            task = self.task_repository.get(task_id)
            return Result.success(TaskResponse.from_entity(task))
        except TaskNotFoundError:
            return Result.failure(Error.not_found("Task", str(task_id)))


@dataclass
class UpdateTaskUseCase:

    task_repository: TaskRepository
    notification_service: NotificationPort

    def execute(self, request: UpdateTaskRequest) -> Result[TaskResponse]:
        try:
            params = request.to_execution_params()
            task = self.task_repository.get(params["task_id"])

            if params.get("title") is not None:
                task.title = params["title"]
            if params.get("description") is not None:
                task.description = params["description"]
            if params.get("status") is not None:
                task.status = params["status"]
            if params.get("priority") is not None:
                task.priority = params["priority"]
                if task.priority == Priority.HIGH:
                    self.notification_service.notify_task_high_priority(task)
            if "deadline" in params:
                task.due_date = params["deadline"]

            self.task_repository.save(task)
            return Result.success(TaskResponse.from_entity(task))

        except TaskNotFoundError:
            return Result.failure(Error.not_found("Task", str(params["task_id"])))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class DeleteTaskUseCase:

    task_repository: TaskRepository

    def execute(self, task_id: UUID) -> Result[DeletionOutcome]:

        try:
            # Verify task exists before deletion
            self.task_repository.get(task_id)
            self.task_repository.delete(task_id)
            return Result.success(DeletionOutcome(task_id))
        except TaskNotFoundError:
            return Result.failure(Error.not_found("Task", str(task_id)))