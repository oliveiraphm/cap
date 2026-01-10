from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from TodoApp.todo_app.interfaces.view_models.project_vm import ProjectViewModel
from TodoApp.todo_app.interfaces.presenters.base import ProjectPresenter
from TodoApp.todo_app.interfaces.view_models.base import OperationResult
from TodoApp.todo_app.application.dtos.project_dtos import CompleteProjectRequest, CreateProjectRequest, UpdateProjectRequest
from TodoApp.todo_app.application.use_cases.project_use_cases import CompleteProjectUseCase, CreateProjectUseCase, GetProjectUseCase, ListProjectsUseCase, UpdateProjectUseCase

@dataclass
class ProjectController:
    
    create_use_case: CreateProjectUseCase
    complete_use_case: CompleteProjectUseCase
    presenter: ProjectPresenter
    get_use_case: GetProjectUseCase
    list_use_case: ListProjectsUseCase
    update_use_case: UpdateProjectUseCase

    def handle_create(self, name: str, description: str = "") -> OperationResult:

        try:
            request = CreateProjectRequest(name=name, description=description)
            result = self.create_use_case.execute(request)

            if result.is_success:
                view_model = self.presenter.present_project(result.value)
                return OperationResult.succeed(view_model)
            
            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)
        
        except ValueError as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)
        
    def handle_complete(self, project_id: str, notes: Optional[str] = None) -> OperationResult:
        try:
            request = CompleteProjectRequest(project_id=project_id, completion_notes=notes)
            result = self.complete_use_case.execute(request)

            if result.is_success:
                view_model = self.presenter.present_project(result.value)
                return OperationResult.succeed(view_model)
            
            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)
        
        except ValueError as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_get(self, project_id: str) -> OperationResult[ProjectViewModel]:
        try:
            result = self.get_use_case.execute(project_id)

            if result.is_success:
                view_model = self.presenter.present_project(result.value)
                return OperationResult.succeed(view_model)

            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)

        except ValueError as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_list(self) -> OperationResult[list[ProjectViewModel]]:

        result = self.list_use_case.execute()

        if result.is_success:
            view_models = [self.presenter.present_project(proj) for proj in result.value]
            return OperationResult.succeed(view_models)

        error_vm = self.presenter.present_error(result.error.message, str(result.error.code.name))
        return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_update(
        self, 
        project_id: str, 
        name: Optional[str] = None, 
        description: Optional[str] = None
    ) -> OperationResult:

        try:
            request = UpdateProjectRequest(
                project_id=project_id,
                name=name,
                description=description
            )
            result = self.update_use_case.execute(request)

            if result.is_success:
                view_model = self.presenter.present_project(result.value)
                return OperationResult.succeed(view_model)

            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)

        except ValueError as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)