from django.db import models
from django.utils import timezone


# Create your models here.
class Task(models.Model):
    PRIORITY_CHOICES = (
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    )
    title = models.CharField(max_length=200)
    due_at = models.DateTimeField(null=True, blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    def is_overdue(self, dt):
        if self.due_at is None:
            return False
        return self.due_at < dt
