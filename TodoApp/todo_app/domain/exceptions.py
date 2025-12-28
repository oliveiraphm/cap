from uuid import UUID

class DomainError(Exception):
    pass

class TaskNotFoundError(DomainError):
    
    def __init__(self, task_id: UUID) -> None:
        self.task_id = task_id
        super().__init__(f"Task with id {task_id} not found")

class ProjectNotFoundError(DomainError):
    def __init__(self, project_id: UUID) -> None:
        self.project_id = project_id
        super().__init__(f"Project with id {project_id} not found")

class ValidationError(DomainError):
    pass

class BusinessRuleViolation(DomainError):
    pass