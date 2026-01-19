from datetime import datetime, timezone
from typing import Optional

from todo_app.domain.value_objects import TaskStatus
from todo_app.application.dtos.project_dtos import CompleteProjectResponse, ProjectResponse
from todo_app.application.dtos.task_dtos import TaskResponse
from todo_app.interfaces.presenters.base import ProjectPresenter, TaskPresenter
from todo_app.interfaces.view_models.base import ErrorViewModel
from todo_app.interfaces.view_models.project_vm import ProjectCompletionViewModel, ProjectViewModel
from todo_app.interfaces.view_models.task_vm import TaskViewModel


class WebTaskPresenter(TaskPresenter):

    def present_task(self, task_response: TaskResponse) -> TaskViewModel:

        return TaskViewModel(
            id=task_response.id,
            title=task_response.title,
            description=task_response.description,
            status_display=task_response.status.value,
            priority_display=task_response.priority.name,
            due_date_display=self._format_due_date(task_response.due_date),
            project_display=task_response.project_id,
            completion_info=self._format_completion_info(
                task_response.completion_date, task_response.completion_notes
            ),
        )

    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:

        return ErrorViewModel(message=error_msg, code=code or "ERROR")

    def _format_due_date(self, due_date: Optional[datetime]) -> str:

        if not due_date:
            return ""

        is_overdue = due_date < datetime.now(timezone.utc)
        date_str = due_date.strftime("%Y-%m-%d")
        return f"Overdue: {date_str}" if is_overdue else date_str

    def _format_completion_info(
        self, completion_date: Optional[datetime], completion_notes: Optional[str]
    ) -> str:

        if not completion_date:
            return ""

        base_info = f"Completed on {completion_date.strftime('%Y-%m-%d %H:%M')}"
        if completion_notes:
            return f"{base_info}\nNotes: {completion_notes}"
        return base_info


class WebProjectPresenter(ProjectPresenter):


    def __init__(self):
        self.task_presenter = WebTaskPresenter()

    def present_project(self, project_response: ProjectResponse) -> ProjectViewModel:

        return ProjectViewModel(
            id=project_response.id,
            name=project_response.name,
            description=project_response.description or "",
            project_type=project_response.project_type.name,
            status_display=project_response.status.value,
            task_count=len(project_response.tasks),
            completed_task_count=sum(
                1 for task in project_response.tasks if task.status == TaskStatus.DONE
            ),
            completion_info=self._format_completion_info(project_response.completion_date),
            tasks=[self.task_presenter.present_task(task) for task in project_response.tasks],
        )

    def present_completion(
        self, completion_response: CompleteProjectResponse
    ) -> ProjectCompletionViewModel:

        return ProjectCompletionViewModel(
            project_id=completion_response.id,
            completion_notes=None,
        )

    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:

        return ErrorViewModel(message=error_msg, code=code or "ERROR")

    def _format_completion_info(self, completion_date: Optional[datetime]) -> str:

        if not completion_date:
            return ""
        return completion_date.strftime("%Y-%m-%d %H:%M")