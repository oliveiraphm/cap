from datetime import timedelta

from TodoApp.todo_app.domain.entities.task import Task
from TodoApp.todo_app.domain.value_objects import Priority


class TaskPriorityCalculator:
    @staticmethod
    def calculate_priority(task: Task) -> Priority:
        if task.due_date is None:
            return task.priority
        
        if task.is_overdue() or task.due_date.time_remaining() <= timedelta(hours=12):
            return Priority.HIGH
        elif task.due_date and task.due_date.time_remaining() <= timedelta(days=2):
            return Priority.MEDIUM
        else:
            return Priority.LOW