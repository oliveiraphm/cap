from abc import ABC, abstractmethod
from typing import Optional

from TodoApp.todo_app.interfaces.view_models.base import ErrorViewModel
from TodoApp.todo_app.application.dtos.project_dtos import CompleteProjectResponse, ProjectResponse
from TodoApp.todo_app.application.dtos.task_dtos import TaskResponse
from TodoApp.todo_app.interfaces.view_models.project_vm import ProjectCompletionViewModel, ProjectViewModel
from TodoApp.todo_app.interfaces.view_models.task_vm import TaskViewModel


class TaskPresenter(ABC):

    @abstractmethod
    def present_task(self, task_response: TaskResponse) -> TaskViewModel:
        pass

    @abstractmethod
    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        pass

class ProjectPresenter(ABC):
    
    @abstractmethod
    def present_project(self, project_response: ProjectResponse) -> ProjectViewModel:

        pass
        
    @abstractmethod
    def present_completion(self, completion_response: CompleteProjectResponse) -> ProjectCompletionViewModel:

        pass
        
    @abstractmethod
    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:

        pass