from dataclasses import dataclass
from TodoApp.todo_app.domain.entities.task import Task
from TodoApp.todo_app.application.service_ports.notifications import NotificationPort

@dataclass
class NotificationRecorder(NotificationPort):
    def __init__(self) -> None:
        self.completed_tasks = []
        self.high_priority_tasks = []
        self.deadline_warnings = []

    def notify_task_completed(self, task: Task) -> None:
        message = f"Task {task.id} has been completed"
        print(f"NOTIFICATION: {message}")
        self.completed_tasks.append(task.id)

    def notify_task_high_priority(self, task: Task) -> None:
        message = f"Task {task.id} has been set to high priority"
        print(f"NOTIFICATION: {message}")
        self.high_priority_tasks.append(task.id)

    def notify_task_deadline_approaching(self, task: Task, days_remaining: int) -> None:
        message = f"Task {task.id} deadline approaching in {days_remaining} days"
        print(f"NOTIFICATIO: {message}")
        self.deadline_warnings.append((task.id, days_remaining))