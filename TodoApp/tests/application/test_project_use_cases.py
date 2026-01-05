from uuid import uuid4
import pytest

from tests.application.conftest import InMemoryProjectRepository, InMemoryTaskRepository, NotificationRecorder
from TodoApp.todo_app.application.common.result import ErrorCode
from TodoApp.todo_app.application.dtos.project_dtos import CreateProjectRequest, CompleteProjectRequest
from TodoApp.todo_app.application.use_cases.project_use_cases import CreateProjectUseCase, CompleteProjectUseCase
from TodoApp.todo_app.domain.entities.project import Project
from TodoApp.todo_app.domain.entities.task import Task
from TodoApp.todo_app.domain.exceptions import BusinessRuleViolation, ValidationError
from TodoApp.todo_app.domain.value_objects import ProjectStatus, TaskStatus

def test_create_project():

    repo = InMemoryProjectRepository()
    use_case = CreateProjectUseCase(repo)
    request = CreateProjectRequest(name="Test Project", description="Test Description")

    result = use_case.execute(request)

    assert result.is_success
    assert result.value.name == "Test Project"
    assert result.value.description == "Test Description"
    assert result.value.status == ProjectStatus.ACTIVE

def test_complete_project_without_tasks():
    project_repo = InMemoryProjectRepository()
    task_repo = InMemoryTaskRepository()
    notify_port = NotificationRecorder()
    use_case = CompleteProjectUseCase(project_repo, task_repo, notify_port)

    project = Project(name="Test Project")
    project_repo.save(project)

    request = CompleteProjectRequest(project_id=str(project.id), completion_notes="All done!")

    result = use_case.execute(request)

    assert result.is_success
    assert result.value.status == ProjectStatus.COMPLETED
    assert result.value.completion_notes == "All done!"
    assert result.value.task_count == 0

def test_complete_project_with_incomplete_tasks():

    project_repo = InMemoryProjectRepository()
    task_repo = InMemoryTaskRepository()
    notify_port = NotificationRecorder()
    use_case = CompleteProjectUseCase(project_repo, task_repo, notify_port)

    project = Project(name="Test Project")
    task = Task(title="Test Task", description="Test")
    project.add_task(task)
    project_repo.save(project)

    request = CompleteProjectRequest(project_id=str(project.id), completion_notes="Done!")

    result = use_case.execute(request)

    assert result.is_success
    assert task.status == TaskStatus.DONE

def test_complete_project_with_completed_tasks():

    project_repo = InMemoryProjectRepository()
    task_repo = InMemoryTaskRepository()
    notify_port = NotificationRecorder()
    use_case = CompleteProjectUseCase(project_repo, task_repo, notify_port)

    project = Project(name="Test Project")
    task = Task(title="Test Task", description="Test")
    task.complete()
    project.add_task(task)
    project_repo.save(project)

    request = CompleteProjectRequest(
        project_id=str(project.id), completion_notes="All done!"
    )

    result = use_case.execute(request)

    assert result.is_success
    assert result.value.status == ProjectStatus.COMPLETED
    assert result.value.task_count == 1


def test_complete_nonexistent_project():

    project_repo = InMemoryProjectRepository()
    task_repo = InMemoryTaskRepository()
    notify_port = NotificationRecorder()
    use_case = CompleteProjectUseCase(project_repo, task_repo, notify_port)

    request = CompleteProjectRequest(
        project_id=str(uuid4()), completion_notes="Done!"
    )

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code.value == "NOT_FOUND"


def test_create_project_handles_validation_error():

    class ValidationErrorProjectRepository(InMemoryProjectRepository):
        def save(self, project):
            raise ValidationError("Invalid project data")

    repo = ValidationErrorProjectRepository()
    use_case = CreateProjectUseCase(repo)
    request = CreateProjectRequest(
        name="Test Project", description="Test Description"
    )

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.VALIDATION_ERROR
    assert "Invalid project data" in result.error.message


def test_create_project_handles_business_rule_violation():

    class BusinessRuleProjectRepository(InMemoryProjectRepository):
        def save(self, project):
            raise BusinessRuleViolation("Project limit exceeded")

    repo = BusinessRuleProjectRepository()
    use_case = CreateProjectUseCase(repo)
    request = CreateProjectRequest(
        name="Test Project", description="Test Description"
    )

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.BUSINESS_RULE_VIOLATION
    assert "Project limit exceeded" in result.error.message


def test_complete_project_handles_validation_error():

    project = Project(name="Test Project")
    task = Task(title="Test Task", description="Test")
    project.add_task(task)

    class ValidationErrorProjectRepository(InMemoryProjectRepository):
        def save(self, project):
            raise ValidationError("Invalid completion state")

    project_repo = ValidationErrorProjectRepository()
    project_repo._projects[project.id] = project
    task_repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()

    use_case = CompleteProjectUseCase(project_repo, task_repo, notifications)
    request = CompleteProjectRequest(
        project_id=str(project.id), completion_notes="Done!"
    )

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.VALIDATION_ERROR
    assert "Invalid completion state" in result.error.message
    assert not notifications.completed_tasks


def test_complete_project_fails_with_malformed_project_id():

    project_repo = InMemoryProjectRepository()

    with pytest.raises(ValueError, match="Invalid project ID format"):
        _ = CompleteProjectRequest(
            project_id="malformed project id",
        )


def test_complete_project_handles_business_rule_violation():
 
    project = Project(name="Test Project")
    task = Task(title="Test Task", description="Test")
    project.add_task(task)

    class BusinessRuleProjectRepository(InMemoryProjectRepository):
        def save(self, project):
            raise BusinessRuleViolation(
                "Cannot complete project in current state"
            )

    project_repo = BusinessRuleProjectRepository()
    project_repo._projects[project.id] = project  # Add project directly
    task_repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()

    use_case = CompleteProjectUseCase(project_repo, task_repo, notifications)
    request = CompleteProjectRequest(
        project_id=str(project.id), completion_notes="Done!"
    )

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.BUSINESS_RULE_VIOLATION
    assert "Cannot complete project in current state" in result.error.message
    assert not notifications.completed_tasks


def test_complete_project_handles_validation_error_from_task():

    project = Project(name="Test Project")
    task = Task(title="Test Task", description="Test")
    project.add_task(task)

    class ValidationErrorTaskRepository(InMemoryTaskRepository):
        def save(self, task):
            raise ValidationError("Invalid task completion state")

    project_repo = InMemoryProjectRepository()
    project_repo._projects[project.id] = project  # Add project directly
    task_repo = ValidationErrorTaskRepository()
    notifications = NotificationRecorder()

    use_case = CompleteProjectUseCase(project_repo, task_repo, notifications)
    request = CompleteProjectRequest(
        project_id=str(project.id), completion_notes="Done!"
    )

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.VALIDATION_ERROR
    assert "Invalid task completion state" in result.error.message
    assert not notifications.completed_tasks


def test_complete_project_rolls_back_on_validation_error():

    project = Project(name="Test Project")
    task1 = Task(title="Task 1", description="Test")
    task2 = Task(title="Task 2", description="Test")
    project.add_task(task1)
    project.add_task(task2)

    class FailingProjectRepository(InMemoryProjectRepository):
        def save(self, project):
            if project.status == ProjectStatus.COMPLETED:
                raise ValidationError("Cannot complete project")
            super().save(project)

    project_repo = FailingProjectRepository()
    task_repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()

    project_repo.save(project)
    task_repo.save(task1)
    task_repo.save(task2)

    use_case = CompleteProjectUseCase(project_repo, task_repo, notifications)
    request = CompleteProjectRequest(
        project_id=str(project.id), completion_notes="Done!"
    )

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.VALIDATION_ERROR

    saved_project = project_repo.get(project.id)
    assert saved_project.status == ProjectStatus.ACTIVE

    for task in [task1, task2]:
        saved_task = task_repo.get(task.id)
        assert saved_task.status == TaskStatus.TODO
        assert saved_task.completed_at is None
        assert saved_task.completion_notes is None


def test_complete_project_rolls_back_on_business_rule_violation():

    project = Project(name="Test Project")
    task1 = Task(title="Task 1", description="Test")
    task2 = Task(title="Task 2", description="Test")
    project.add_task(task1)
    project.add_task(task2)

    class FailingTaskRepository(InMemoryTaskRepository):
        def save(self, task):
            if (
                task.status == TaskStatus.DONE and task.title == "Task 2"
            ):
                raise BusinessRuleViolation("Task limit reached")
            super().save(task)

    project_repo = InMemoryProjectRepository()
    task_repo = FailingTaskRepository()
    notifications = NotificationRecorder()

    project_repo.save(project)
    task_repo.save(task1)
    task_repo.save(task2)

    use_case = CompleteProjectUseCase(project_repo, task_repo, notifications)
    request = CompleteProjectRequest(
        project_id=str(project.id), completion_notes="Done!"
    )

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.BUSINESS_RULE_VIOLATION

    saved_project = project_repo.get(project.id)
    assert saved_project.status == ProjectStatus.ACTIVE

    for task in [task1, task2]:
        saved_task = task_repo.get(task.id)
        assert saved_task.status == TaskStatus.TODO
        assert saved_task.completed_at is None
        assert saved_task.completion_notes is None

    assert not notifications.completed_tasks