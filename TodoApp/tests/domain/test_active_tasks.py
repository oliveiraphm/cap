from tests.application.conftest import InMemoryTaskRepository

from todo_app.domain.entities.task import Task
from todo_app.domain.value_objects import TaskStatus

def test_get_active_tasks_empty_repository():
    repo = InMemoryTaskRepository()
    tasks = repo.get_active_tasks()
    assert len(tasks) == 0

def test_get_active_tasks_only_active():
    repo = InMemoryTaskRepository()

    task1 = Task(title="Task 1", description="Test")
    task2 = Task(title="Task 2", description="Test")
    task3 = Task(title="Task 3", description="Test")

    repo.save(task1)
    repo.save(task2)
    repo.save(task3)

    tasks = repo.get_active_tasks()
    assert len(tasks) == 3
    assert all(task.status == TaskStatus.TODO for task in tasks)

def test_get_active_tasks_mixed_status():
    repo = InMemoryTaskRepository()

    todo_task = Task(title="Todo Task", description="Test")
    in_progress_task = Task(title="In Progress Task", description="Test")
    in_progress_task.start()
    completed_task = Task(title="Completed Task", description="Test")
    completed_task.complete()

    repo.save(todo_task)
    repo.save(in_progress_task)
    repo.save(completed_task)

    tasks = repo.get_active_tasks()
    assert len(tasks) == 2
    assert completed_task not in tasks
    assert all(task.status != TaskStatus.DONE for task in tasks)

def test_get_active_tasks_only_completed():

    repo = InMemoryTaskRepository()

    task1 = Task(title="Task 1", description="Test")
    task2 = Task(title="Task 2", description="Test")
    task3 = Task(title="Task 3", description="Test")

    for task in [task1, task2, task3]:
        task.complete()
        repo.save(task)

    tasks = repo.get_active_tasks()
    assert len(tasks) == 0

def test_get_active_tasks_after_completion():

    repo = InMemoryTaskRepository()

    task1 = Task(title="Task 1", description="Test")
    task2 = Task(title="Task 2", description="Test")
    task3 = Task(title="Task 3", description="Test")

    repo.save(task1)
    repo.save(task2)
    repo.save(task3)

    assert len(repo.get_active_tasks()) == 3

    task1.complete()
    task3.complete()
    repo.save(task1)
    repo.save(task3)

    active_tasks = repo.get_active_tasks()
    assert len(active_tasks) == 1
    assert task2 in active_tasks