from uuid import uuid4
import pytest

from tests.application.conftest import InMemoryTaskRepository, InMemoryProjectRepository, NotificationRecorder
from TodoApp.todo_app.application.common.result import ErrorCode
from TodoApp.todo_app.application.dtos.task_dtos import CreateTaskRequest, CompleteTaskRequest, SetTaskPriorityRequest
from TodoApp.todo_app.application.use_cases.task_use_cases import CreateTaskUseCase, CompleteTaskUseCase, SetTaskPriorityUseCase
from TodoApp.todo_app.domain.entities.project import Project
from TodoApp.todo_app.domain.entities.task import Task
from TodoApp.todo_app.domain.exceptions import BusinessRuleViolation, ValidationError
from TodoApp.todo_app.domain.value_objects import Priority, TaskStatus


def test_create_task_basic():

    repo = InMemoryTaskRepository()
    project_repo = InMemoryProjectRepository()
    use_case = CreateTaskUseCase(repo, project_repo)

    request = CreateTaskRequest(title="Test Task", description="Test Description")

    result = use_case.execute(request)

    assert result.is_success
    assert result.value.title == "Test Task"
    assert result.value.description == "Test Description"
    assert result.value.status == TaskStatus.TODO
    assert result.value.priority == Priority.MEDIUM


def test_create_task_with_project():

    task_repo = InMemoryTaskRepository()
    project_repo = InMemoryProjectRepository()
    use_case = CreateTaskUseCase(task_repo, project_repo)

    project = Project(name="Test Project")
    project_repo.save(project)

    request = CreateTaskRequest(
        title="Test Task",
        description="Test Description",
        project_id=str(project.id),
    )

    result = use_case.execute(request)

    assert result.is_success
    assert result.value.project_id == str(project.id)


def test_create_task_with_invalid_project():

    task_repo = InMemoryTaskRepository()
    project_repo = InMemoryProjectRepository()
    use_case = CreateTaskUseCase(task_repo, project_repo)

    request = CreateTaskRequest(
        title="Test Task",
        description="Test Description",
        project_id=str(uuid4()),
    )

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code.value == "NOT_FOUND"


def test_complete_task():

    repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()
    use_case = CompleteTaskUseCase(repo, notifications)

    task = Task(title="Test Task", description="Test Description")
    repo.save(task)

    request = CompleteTaskRequest(task_id=str(task.id), completion_notes="Done!")

    result = use_case.execute(request)

    assert result.is_success
    assert result.value.status == TaskStatus.DONE
    assert result.value.completion_notes == "Done!"
    assert task.id in notifications.completed_tasks


def test_complete_nonexistent_task():

    repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()
    use_case = CompleteTaskUseCase(repo, notifications)

    request = CompleteTaskRequest(task_id=str(uuid4()), completion_notes="Done!")

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code.value == "NOT_FOUND"
    assert not notifications.completed_tasks


def test_set_task_priority():

    repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()
    use_case = SetTaskPriorityUseCase(repo, notifications)

    task = Task(title="Test Task", description="Test Description")
    repo.save(task)

    request = SetTaskPriorityRequest(task_id=str(task.id), priority="HIGH")

    result = use_case.execute(request)

    assert result.is_success
    assert result.value.priority == Priority.HIGH
    assert task.id in notifications.high_priority_tasks


def test_set_task_invalid_priority():

    repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()
    use_case = SetTaskPriorityUseCase(repo, notifications)

    task = Task(title="Test Task", description="Test Description")
    repo.save(task)

    with pytest.raises(ValueError) as exc_info:
        SetTaskPriorityRequest(task_id=str(task.id), priority="INVALID")

    assert "Priority must be one of" in str(exc_info.value)


def test_complete_task_handles_validation_error():

    task = Task(title="Test Task", description="Test Description")

    class ValidationErrorTaskRepository(InMemoryTaskRepository):
        def save(self, task):
            raise ValidationError("Invalid completion state")

    repo = ValidationErrorTaskRepository()
    repo._tasks[task.id] = task
    notifications = NotificationRecorder()
    use_case = CompleteTaskUseCase(repo, notifications)

    request = CompleteTaskRequest(task_id=str(task.id), completion_notes="Done!")

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.VALIDATION_ERROR
    assert "Invalid completion state" in result.error.message
    assert not notifications.completed_tasks


def test_complete_task_handles_business_rule_violation():

    task = Task(title="Test Task", description="Test Description")

    class BusinessRuleTaskRepository(InMemoryTaskRepository):
        def save(self, task):
            raise BusinessRuleViolation("Cannot complete task in current state")

    repo = BusinessRuleTaskRepository()
    repo._tasks[task.id] = task
    notifications = NotificationRecorder()
    use_case = CompleteTaskUseCase(repo, notifications)

    request = CompleteTaskRequest(task_id=str(task.id), completion_notes="Done!")

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.BUSINESS_RULE_VIOLATION
    assert "Cannot complete task in current state" in result.error.message
    assert not notifications.completed_tasks


def test_create_task_request_validates_project_id_format():

    valid_request = CreateTaskRequest(
        title="Test Task",
        description="Test Description",
        project_id="123e4567-e89b-12d3-a456-426614174000",
    )
    assert valid_request.project_id == "123e4567-e89b-12d3-a456-426614174000"

    with pytest.raises(ValueError, match="Invalid project ID format"):
        CreateTaskRequest(
            title="Test Task",
            description="Test Description",
            project_id="not-a-uuid",
        )

    no_project_request = CreateTaskRequest(
        title="Test Task", description="Test Description", project_id=None
    )
    assert no_project_request.project_id is None


def test_create_task_handles_validation_error():

    class ValidationErrorTaskRepository(InMemoryTaskRepository):
        def save(self, task):
            raise ValidationError("Invalid task data")

    task_repo = ValidationErrorTaskRepository()
    project_repo = InMemoryProjectRepository()
    use_case = CreateTaskUseCase(task_repo, project_repo)

    request = CreateTaskRequest(title="Test Task", description="Test Description")

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.VALIDATION_ERROR
    assert "Invalid task data" in result.error.message


def test_create_task_handles_business_rule_violation():

    class BusinessRuleTaskRepository(InMemoryTaskRepository):
        def save(self, task):
            raise BusinessRuleViolation("Task limit exceeded")

    task_repo = BusinessRuleTaskRepository()
    project_repo = InMemoryProjectRepository()
    use_case = CreateTaskUseCase(task_repo, project_repo)

    request = CreateTaskRequest(title="Test Task", description="Test Description")

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.BUSINESS_RULE_VIOLATION
    assert "Task limit exceeded" in result.error.message


def test_create_task_handles_validation_error_with_project():

    project = Project(name="Test Project")

    class ValidationErrorTaskRepository(InMemoryTaskRepository):
        def save(self, task):
            raise ValidationError("Invalid task data")

    task_repo = ValidationErrorTaskRepository()
    project_repo = InMemoryProjectRepository()
    project_repo._projects[project.id] = project  # Add project directly
    use_case = CreateTaskUseCase(task_repo, project_repo)

    request = CreateTaskRequest(
        title="Test Task",
        description="Test Description",
        project_id=str(project.id),
    )

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.VALIDATION_ERROR
    assert "Invalid task data" in result.error.message


def test_complete_task_rolls_back_on_validation_error():
    task = Task(title="Test Task", description="Test Description")

    class FailingTaskRepository(InMemoryTaskRepository):
        def save(self, task):
            if task.status == TaskStatus.DONE:
                raise ValidationError("Cannot complete task")
            super().save(task)

    repo = FailingTaskRepository()
    notifications = NotificationRecorder()

    repo.save(task)

    use_case = CompleteTaskUseCase(repo, notifications)
    request = CompleteTaskRequest(task_id=str(task.id), completion_notes="Done!")

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.VALIDATION_ERROR

    saved_task = repo.get(task.id)
    assert saved_task.status == TaskStatus.TODO
    assert saved_task.completed_at is None
    assert saved_task.completion_notes is None

    assert not notifications.completed_tasks


def test_complete_task_rolls_back_on_business_rule_violation():

    task = Task(title="Test Task", description="Test Description")

    class FailingTaskRepository(InMemoryTaskRepository):
        def save(self, task):
            if task.status == TaskStatus.DONE:
                raise BusinessRuleViolation("Task completion limit reached")
            super().save(task)

    repo = FailingTaskRepository()
    notifications = NotificationRecorder()

    repo.save(task)

    use_case = CompleteTaskUseCase(repo, notifications)
    request = CompleteTaskRequest(task_id=str(task.id), completion_notes="Done!")

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.BUSINESS_RULE_VIOLATION

    saved_task = repo.get(task.id)
    assert saved_task.status == TaskStatus.TODO
    assert saved_task.completed_at is None
    assert saved_task.completion_notes is None

    assert not notifications.completed_tasks


def test_complete_task_maintains_state_on_successful_completion():
    task = Task(title="Test Task", description="Test Description")

    repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()

    repo.save(task)

    use_case = CompleteTaskUseCase(repo, notifications)
    completion_notes = "Done!"
    request = CompleteTaskRequest(task_id=str(task.id), completion_notes=completion_notes)

    result = use_case.execute(request)

    assert result.is_success

    saved_task = repo.get(task.id)
    assert saved_task.status == TaskStatus.DONE
    assert saved_task.completed_at is not None
    assert saved_task.completion_notes == completion_notes

    assert str(task.id) in [str(t_id) for t_id in notifications.completed_tasks]


def test_create_task_with_nonexistent_project():

    task_repo = InMemoryTaskRepository()
    project_repo = InMemoryProjectRepository()
    use_case = CreateTaskUseCase(task_repo, project_repo)

    request = CreateTaskRequest(
        title="Test Task",
        description="Test Description",
        project_id="123e4567-e89b-12d3-a456-426614174000",
    )

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.NOT_FOUND
    assert "Project with id 123e4567-e89b-12d3-a456-426614174000 not found" in result.error.message


def test_create_task_fails_with_malformed_project_id():

    with pytest.raises(ValueError, match="Invalid project ID format"):
        _ = CreateTaskRequest(
            title="Test Task",
            description="Test Description",
            project_id="malformed project id",
        )


def test_set_task_priority_fails_with_malformed_task_id():

    with pytest.raises(ValueError, match="Invalid task ID format"):
        _ = SetTaskPriorityRequest(
            task_id="malformed project id",
            priority="HIGH",
        )


def test_set_task_priority_handles_validation_error():

    task = Task(title="Test Task", description="Test Description")

    class ValidationErrorTaskRepository(InMemoryTaskRepository):
        def save(self, task):
            raise ValidationError("Invalid priority state")

    repo = ValidationErrorTaskRepository()
    repo._tasks[task.id] = task
    notifications = NotificationRecorder()

    use_case = SetTaskPriorityUseCase(repo, notifications)
    request = SetTaskPriorityRequest(task_id=str(task.id), priority="HIGH")

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.VALIDATION_ERROR
    assert "Invalid priority state" in result.error.message
    assert not notifications.high_priority_tasks