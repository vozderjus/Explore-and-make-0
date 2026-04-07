from django.db import models
from django.conf import settings

PRIORITY_CHOICES = (
    ("LOW", "Низкий"),
    ("MEDIUM", "Средний"),
    ("HIGH", "Высокий"),
    ("CRITICAL", "Критичный"),
)

STATUS_CHOICES = (
    ("NEW", "Новая"),
    ("IN_PROGRESS", "В работе"),
    ("IN_REVIEW", "На проверке"),
    ("DONE", "Выполнена"),
)

class Project(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="project_memberships",
    )


class Task(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    title = models.CharField(max_length=64),
    description = models.TextField()
    priority = models.CharField(choices=PRIORITY_CHOICES.choices, default=PRIORITY_CHOICES.MEDIUM)
    status = models.CharField(choices=STATUS_CHOICES.choices, default=STATUS_CHOICES.NEW)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    performers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="related_tasks",
    )
