import json 
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
from uuid import UUID

from TodoApp.todo_app.domain.entities.task import Task
from TodoApp.todo_app.domain.entities.project import Project
from TodoApp.todo_app.domain.exceptions import TaskNotFoundError, ProjectNotFoundError, InboxNotFoundError
from TodoApp.todo_app.domain.value_objects import ProjectType, TaskStatus, ProjectStatus, Priority, Deadline
from TodoApp.todo_app.application.repositories.task_repository import TaskRepository
from TodoApp.todo_app.application.repositories.project_repository import ProjectRepository

class JsonEncoder(json.JSONDecoder):

    def default(self, obj: Any) -> Any:
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, (TaskStatus, ProjectStatus, Priority)):
            return obj.name
        return super().default(obj)
    
class FileTaskRepository(TaskRepository):

    def __init__(self, data_dir: Path):
        self.tasks_file = data_dir / "tasks.json"
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        if not self.tasks_file.exists():
            self.tasks_file.write_text("[]")
    
    def _load_tasks(self) -> list[Dict[str, Any]]:
        return json.loads(self.tasks_file.read_text())
    
    def _save_tasks(self, tasks: list[Dict[str, Any]]) -> None:
        self.tasks_file.write_text(json.dumps(tasks, indent=2, cls=JsonEncoder))

    def _task_to_dict(self, task: Task) -> Dict[str, Any]:

        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "project_id": task.project_id,
            "due_date": task.due_date.due_date if task.due_date else None,
            "priority": task.priority.name,
            "status": task.status.name,
            "completed_at": task.completed_at,
            "completion_notes": task.completion_notes,
        }
    

    def _dict_to_task(self, data: Dict[str, Any]) -> Task:

        task = Task(
            title=data["title"],
            description=data["description"],
            project_id=UUID(data["project_id"]),
            priority=Priority[data["priority"]],
        )

        if data["due_date"]:
            task.due_date = Deadline(datetime.fromisoformat(data["due_date"]))
        task.status = TaskStatus[data["status"]]
        if data["completed_at"]:
            task.completed_at = datetime.fromisoformat(data["completed_at"])
        task.completion_notes = data["completion_notes"]

        task.id = UUID(data["id"])

        return task

    def get(self, task_id: UUID) -> Task:

        tasks = self._load_tasks()
        for task_data in tasks:
            if UUID(task_data["id"]) == task_id:
                return self._dict_to_task(task_data)
        raise TaskNotFoundError(task_id)

    def save(self, task: Task) -> None:
        tasks = self._load_tasks()

        updated = False
        for i, task_data in enumerate(tasks):
            if UUID(task_data["id"]) == task.id:
                tasks[i] = self._task_to_dict(task)
                updated = True
                break

        if not updated:
            tasks.append(self._task_to_dict(task))

        self._save_tasks(tasks)

    def delete(self, task_id: UUID) -> None:

        tasks = self._load_tasks()
        tasks = [t for t in tasks if UUID(t["id"]) != task_id]
        self._save_tasks(tasks)

    def find_by_project(self, project_id: UUID) -> Sequence[Task]:

        tasks = self._load_tasks()
        return [self._dict_to_task(t) for t in tasks if UUID(t["project_id"]) == project_id]

    def get_active_tasks(self) -> Sequence[Task]:

        tasks = self._load_tasks()
        return [self._dict_to_task(t) for t in tasks if t["status"] != TaskStatus.DONE.name]


class FileProjectRepository(ProjectRepository):

    def __init__(self, data_dir: Path):
        self.projects_file = data_dir / "projects.json"
        self._ensure_file_exists()
        self._task_repo = None

        inbox = self._fetch_inbox()
        if not inbox:
            inbox = Project.create_inbox()
            self.save(inbox)

    def set_task_repository(self, task_repo: TaskRepository) -> None:
        self._task_repo = task_repo

    def _ensure_file_exists(self) -> None:

        if not self.projects_file.exists():
            self.projects_file.write_text("[]")

    def _load_projects(self) -> list[Dict[str, Any]]:

        return json.loads(self.projects_file.read_text())

    def _save_projects(self, projects: list[Dict[str, Any]]) -> None:

        self.projects_file.write_text(json.dumps(projects, indent=2, cls=JsonEncoder))

    def _project_to_dict(self, project: Project) -> Dict[str, Any]:

        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "project_type": project.project_type.name,
            "status": project.status.name,
            "completed_at": project.completed_at,
            "completion_notes": project.completion_notes,
        }

    def _dict_to_project(self, data: Dict[str, Any]) -> Project:

        if data.get("project_type") == ProjectType.INBOX.name:
            project = Project.create_inbox()
        else:
            project = Project(name=data["name"], description=data["description"])

        project.status = ProjectStatus[data["status"]]
        if data["completed_at"]:
            project.completed_at = datetime.fromisoformat(data["completed_at"])
        project.completion_notes = data["completion_notes"]

        project.id = UUID(data["id"])

        return project

    def get(self, project_id: UUID) -> Project:

        projects = self._load_projects()
        for project_data in projects:
            if UUID(project_data["id"]) == project_id:
                project = self._dict_to_project(project_data)

                if self._task_repo:
                    self._load_project_tasks(project)
                return project
        raise ProjectNotFoundError(project_id)

    def get_all(self) -> List[Project]:

        projects = [self._dict_to_project(p) for p in self._load_projects()]

        if self._task_repo:
            for project in projects:
                self._load_project_tasks(project)
        return projects

    def save(self, project: Project) -> None:

        projects = self._load_projects()

        updated = False
        for i, project_data in enumerate(projects):
            if UUID(project_data["id"]) == project.id:
                projects[i] = self._project_to_dict(project)
                updated = True
                break

        if not updated:
            projects.append(self._project_to_dict(project))

        self._save_projects(projects)

        for task in project.tasks:
            self._task_repo.save(task)

    def delete(self, project_id: UUID) -> None:

        for task in self._task_repo.find_by_project(project_id):
            self._task_repo.delete(task.id)

        projects = self._load_projects()
        projects = [p for p in projects if UUID(p["id"]) != project_id]
        self._save_projects(projects)

    def _fetch_inbox(self) -> Optional[Project]:

        projects = self._load_projects()
        for project_data in projects:
            if project_data.get("project_type") == ProjectType.INBOX.name:
                return self._dict_to_project(project_data)
        return None

    def get_inbox(self) -> Project:

        inbox = self._fetch_inbox()
        if not inbox:
            raise InboxNotFoundError("The Inbox project was not found")
        return inbox

    def _load_project_tasks(self, project: Project) -> None:

        try:

            project._tasks.clear()


            tasks = self._task_repo.find_by_project(project.id)

            for task in tasks:
                project._tasks[task.id] = task
        except Exception as e:
            
            print(f"Error loading tasks for project {project.id}: {str(e)}")