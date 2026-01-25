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

import logging

logger = logging.getLogger(__name__)

@dataclass
class CompleteTaskUseCase:
    
    task_repository: TaskRepository
    notification_service: NotificationPort
    
    def execute(self, request: CompleteTaskRequest) -> Result:

        try:
            params = request.to_execution_params()
            logger.info("Completing task", extra={"context": {"task_id": str(params["task_id"])}})
            task = self.task_repository.get(params["task_id"])

            task_snapshot = deepcopy(task)

            try: 
                task.complete(notes=params["completion_notes"])
                self.task_repository.save(task)
                self.notification_service.notify_task_completed(task)

                logger.info(
                    "Task completed successfully",
                    extra={
                        "context": {
                            "task_id": str(task.id),
                            "completion_notes": params["completion_notes"],
                        }
                    },
                )

                return Result.success(TaskResponse.from_entity(task))
            
            except (ValidationError, BusinessRuleViolation) as e:
                logger.error(
                    "Failed to complete task",
                    extra={"context": {"task_id": str(task.id), "error": str(e)}},
                )
                self.task_repository.save(task_snapshot)
                raise
        
        except TaskNotFoundError:
            logger.error("Task not found", extra={"context": {"task_id": str(params["task_id"])}})
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
            logger.info(
                "Creating new task",
                extra={"context": {"title": request.title, "project_id": request.project_id}},
            )
 
            params = request.to_execution_params()
            project_id = params.get("project_id")
            
            if not project_id:
                project_id = self.project_repository.get_inbox().id
            else:
                try:
                    self.project_repository.get(project_id)  # Verify exists
                except ProjectNotFoundError:
                    logger.error(
                        "Project not found", extra={"context": {"project_id": str(project_id)}}
                    )
                    return Result.failure(Error.not_found("Project", str(project_id)))

            task = Task(
                title=params["title"],
                description=params["description"],
                project_id=project_id,
                due_date=params.get("deadline"),
                priority=params.get("priority", Priority.MEDIUM),
            )

            self.task_repository.save(task)

            logger.info(
                "Task created successfully",
                extra={
                    "context": {
                        "task_id": str(task.id),
                        "project_id": str(project_id),
                        "title": task.title,
                        "priority": task.priority.name,
                    }
                },
            )

            return Result.success(TaskResponse.from_entity(task))

        except ValidationError as e:
            logger.error("Task creation validation error", extra={"context": {"error": str(e)}})
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            logger.error(
                "Task creation business rule violation", extra={"context": {"error": str(e)}}
            )
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

    def execute(self, task_id: UUID) -> Result:

        try:
            logger.info("Retrieving task details", extra={"context": {"task_id": str(task_id)}})
            task = self.task_repository.get(task_id)
            return Result.success(TaskResponse.from_entity(task))
        except TaskNotFoundError:
            logger.error("Task not found", extra={"context": {"task_id": str(task_id)}})
            return Result.failure(Error.not_found("Task", str(task_id)))


@dataclass
class UpdateTaskUseCase:

    task_repository: TaskRepository
    notification_service: NotificationPort

    def execute(self, request: UpdateTaskRequest) -> Result[TaskResponse]:
        try:
            params = request.to_execution_params()
            logger.info("Updating task", extra={"context": {"task_id": str(params["task_id"])}})
            task = self.task_repository.get(params["task_id"])

            task_snapshot = deepcopy(task)

            try:
                if "title" in params:
                    task.update_title(params["title"])
                if "description" in params:
                    task.update_description(params["description"])
                if "priority" in params:
                    task.update_priority(Priority(params["priority"]))
                if "due_date" in params:
                    task.update_due_date(params["due_date"])

                self.task_repository.save(task)
                logger.info(
                    "Task updated successfully",
                    extra={
                        "context": {
                            "task_id": str(task.id),
                            "updated_fields": [k for k in params.keys() if k != "task_id"],
                        }
                    },
                )
                return Result.success(TaskResponse.from_entity(task))

            except (ValidationError, BusinessRuleViolation) as e:
                logger.error(
                    "Failed to update task",
                    extra={"context": {"task_id": str(task.id), "error": str(e)}},
                )
                self.task_repository.save(task_snapshot)
                raise

        except TaskNotFoundError:
            logger.error("Task not found", extra={"context": {"task_id": str(params["task_id"])}})
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
            logger.info("Deleting task", extra={"context": {"task_id": str(task_id)}})
            self.task_repository.get(task_id)
            self.task_repository.delete(task_id)
            logger.info("Task deleted successfully", extra={"context": {"task_id": str(task_id)}})
            return Result.success(DeletionOutcome(task_id))
        except TaskNotFoundError:
            logger.error("Task not found", extra={"context": {"task_id": str(task_id)}})
            return Result.failure(Error.not_found("Task", str(task_id)))