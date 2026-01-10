from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TaskViewModel:

    id: str
    title: str
    description: str
    status_display: str
    priority_display: str
    due_date_display: Optional[str]
    project_display: Optional[str]
    completion_info: Optional[str]