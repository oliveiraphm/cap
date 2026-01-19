from dataclasses import dataclass

from todo_app.infrastructure.notifications.factory import create_notification_service
from todo_app.application.service_ports.notifications import NotificationPort
from todo_app.application.repositories.project_repository import ProjectRepository
from todo_app.application.repositories.task_repository import TaskRepository
from todo_app.interfaces.presenters.base import ProjectPresenter, TaskPresenter
from todo_app.application.use_cases.project_use_cases import CompleteProjectUseCase, CreateProjectUseCase, GetProjectUseCase, ListProjectsUseCase, UpdateProjectUseCase
from todo_app.application.use_cases.task_use_cases import CompleteTaskUseCase, CreateTaskUseCase, DeleteTaskUseCase, GetTaskUseCase, UpdateTaskUseCase

from todo_app.interfaces.controllers.project_controller import ProjectController
from todo_app.interfaces.controllers.task_controller import TaskController
from todo_app.infrastructure.repository_factory import create_repositories

def create_application(
    notification_service: NotificationPort,
    task_presenter: TaskPresenter,
    project_presenter: ProjectPresenter,
) -> "Application":
    
    task_repository, project_repository = create_repositories()

    notification_service = create_notification_service()

    return Application(
        task_repository=task_repository,
        project_repository=project_repository,
        notification_service=notification_service,
        task_presenter=task_presenter,
        project_presenter=project_presenter,
    )

@dataclass
class Application:

    task_repository: TaskRepository
    project_repository: ProjectRepository
    notification_service: NotificationPort
    task_presenter: TaskPresenter
    project_presenter: ProjectPresenter

    def __post_init__(self):

        self.create_task_use_case = CreateTaskUseCase(self.task_repository, self.project_repository)

        self.complete_task_use_case = CompleteTaskUseCase(
            self.task_repository, self.notification_service
        )

        self.get_task_use_case = GetTaskUseCase(self.task_repository)

        self.create_project_use_case = CreateProjectUseCase(self.project_repository)

        self.complete_project_use_case = CompleteProjectUseCase(
            self.project_repository, self.task_repository, self.notification_service
        )

        self.get_project_use_case = GetProjectUseCase(self.project_repository)

        self.list_projects_use_case = ListProjectsUseCase(self.project_repository)

        self.delete_task_use_case = DeleteTaskUseCase(self.task_repository)
        self.update_task_use_case = UpdateTaskUseCase(
            self.task_repository, self.notification_service
        )

        self.update_project_use_case = UpdateProjectUseCase(self.project_repository)

        self.task_controller = TaskController(
            create_use_case=self.create_task_use_case,
            complete_use_case=self.complete_task_use_case,
            update_use_case=self.update_task_use_case,
            delete_use_case=self.delete_task_use_case,
            get_use_case=self.get_task_use_case,
            presenter=self.task_presenter,
        )

        self.project_controller = ProjectController(
            create_use_case=self.create_project_use_case,
            complete_use_case=self.complete_project_use_case,
            get_use_case=self.get_project_use_case,
            list_use_case=self.list_projects_use_case,
            update_use_case=self.update_project_use_case,
            presenter=self.project_presenter,
        )