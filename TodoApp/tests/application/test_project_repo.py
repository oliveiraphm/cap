from uuid import UUID
import pytest

from tests.application.conftest import InMemoryProjectRepository
from TodoApp.todo_app.domain.entities.project import Project
from TodoApp.todo_app.domain.exceptions import ProjectNotFoundError

def test_project_repository_delete():

    repo = InMemoryProjectRepository()
    project = Project(name="Test Project")
    repo.save(project)

    assert repo.get(project.id) == project

    repo.delete(project.id)

    with pytest.raises(ProjectNotFoundError):
        repo.get(project.id)

def test_project_repository_delete_nonexistent():
    repo = InMemoryProjectRepository()
    random_id = UUID("123e4567-e89b-12d3-a456-426614174000")
    
    repo.delete(random_id)

def test_project_repository_delete_and_recreate():

    repo = InMemoryProjectRepository()

    project1 = Project(name="Test Project")
    repo.save(project1)
    repo.delete(project1.id)

    project2 = Project(name="Test Project")
    repo.save(project2)

    saved_project = repo.get(project2.id)
    assert saved_project == project2
    assert saved_project.id != project1.id

