from abc import ABC, abstractmethod
from TodoApp.todo_app.domain.entities.task import Task

class NotificationPort(ABC):

    @abstractmethod
    def notify_task_completed(self, task: Task) -> None:
        pass

    @abstractmethod
    def notify_task_high_priority(self, task: Task) -> None:
        pass

    @abstractmethod
    def notify_task_deadline_approaching(self, task: Task, days_remaining: int) -> None:
        pass