from django.test import TestCase
from django.utils import timezone
from datetime import datetime
from todo.models import Task

class TaskIsOverdueNoneTestCase(TestCase):
    def test_is_overdue_none(self):
        current = timezone.make_aware(datetime(2024, 7, 1, 0, 0, 0))
        task = Task(title='task1', due_at=None)
        task.save()
        self.assertFalse(task.is_overdue(current))