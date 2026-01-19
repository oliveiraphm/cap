from datetime import datetime, timedelta, timezone

import pytest
from freezegun import freeze_time

from todo_app.domain.entities.task import Task
from todo_app.domain.services.task_priority_calculator import TaskPriorityCalculator
from todo_app.domain.value_objects import Deadline, Priority

class TestDeadline:
    def test_create_valid_future_deadline(self):
        future_date = datetime.now(timezone.utc) + timedelta(days=1)
        deadline = Deadline(future_date)
        assert deadline.due_date == future_date

    def test_reject_past_deadline(self):
        past_date = datetime.now(timezone.utc) - timedelta(days=1)
        with pytest.raises(ValueError, match="Deadline cannot be in the past"):
            Deadline(past_date)

    @freeze_time("2024-01-01 12:00:00+00:00")
    def test_is_overdue(self):
        future_date = datetime.now(timezone.utc) + timedelta(days=1)
        deadline = Deadline(future_date)
        assert not deadline.is_overdue()

        with freeze_time("2024-01-03 12:00:00+00:00"):
            assert deadline.is_overdue()

    @freeze_time("2024-01-01 12:00:00+00:00")
    def test_time_remaining(self):
        due_date = datetime.now(timezone.utc) + timedelta(days=2)
        deadline = Deadline(due_date)
        
        remaining = deadline.time_remaining()
        assert abs(remaining - timedelta(days=2)) < timedelta(seconds=1)

        with freeze_time("2024-01-04 12:00:00+00:00"):
            remaining = deadline.time_remaining()
            assert remaining == timedelta(0)
    
    @freeze_time("2024-01-01 12:00:00+00:00")
    def test_is_approaching(self):
        base_time = datetime.now(timezone.utc)
        far_date = base_time + timedelta(days=5)
        near_date = base_time + timedelta(hours=12)
        very_near_date = base_time + timedelta(hours=1)

        far_deadline = Deadline(far_date)
        near_deadline = Deadline(near_date)
        very_near_deadline = Deadline(very_near_date)

        assert not far_deadline.is_approaching()
        assert near_deadline.is_approaching()
        assert very_near_deadline.is_approaching()

        custom_threshold = timedelta(hours=2)
        assert not near_deadline.is_approaching(custom_threshold)
        assert very_near_deadline.is_approaching(custom_threshold)

class TestTaskPriorityCalculator:
    @freeze_time("2024-01-01 12:00:00+00:00")
    def test_calculate_priority_overdue(self):
        due_date = datetime.now(timezone.utc) + timedelta(days=1)
        task = Task(
            title="Test Task",
            description="Test Description",
            due_date=Deadline(due_date),
        )
    
        with freeze_time("2024-01-03 12:00:00+00:00"):
            priority = TaskPriorityCalculator.calculate_priority(task)
            assert priority == Priority.HIGH
    
    @freeze_time("2024-01-01 12:00:00+00:00")
    def test_calculate_priority_approaching_deadline(self):
        due_date = datetime.now(timezone.utc) + timedelta(days=2)
        task = Task(
            title="Test Task",
            description="Test Description",
            due_date=Deadline(due_date),
        )

        priority = TaskPriorityCalculator.calculate_priority(task)
        assert priority == Priority.MEDIUM

    @freeze_time("2024-01-01 12:00:00+00:00")
    def test_calculate_priority_far_deadline(self):
        due_date = datetime.now(timezone.utc) + timedelta(days=5)
        task = Task(
            title="Test Task",
            description="Test Description",
            due_date=Deadline(due_date),
        )

        priority = TaskPriorityCalculator.calculate_priority(task)
        assert priority == Priority.LOW

    def test_calculate_priority_no_deadline(self):
        task = Task(title="Test Task", description="Test Description")
        expected_priority = task.priority
        priority = TaskPriorityCalculator.calculate_priority(task)
        assert priority == expected_priority

    @pytest.mark.parametrize(
        "days_until_due,expected_priority",
        [

            (0.5, Priority.HIGH),
            (1, Priority.MEDIUM),
            (2, Priority.MEDIUM),
            (3, Priority.LOW),
            (7, Priority.LOW),

        ],
    )
    @freeze_time("2024-01-01 12:00:00+00:00")
    def test_priority_thresholds(self, days_until_due, expected_priority):
        due_date = datetime.now(timezone.utc) + timedelta(days=days_until_due)
        task = Task(
            title="Test Task",
            description="Test Description",
            due_date=Deadline(due_date),
        )
        priority = TaskPriorityCalculator.calculate_priority(task)
        assert priority == expected_priority