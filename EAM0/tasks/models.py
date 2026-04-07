from django.db import models
from django.conf import settings

class TaskStatus(models.TextChoices):
    NEW = 'new', 'Новая'
    IN_PROGRESS = 'in_progress', 'В работе'
    IN_REVIEW = 'in_review', 'На проверке'
    DONE = 'done', 'Выполнена'


class TaskPriority(models.TextChoices):
    LOW = 'low', 'Низкий'
    MEDIUM = 'medium', 'Средний'
    HIGH = 'high', 'Высокий'
    CRITICAL = 'critical', 'Критический'

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
    priority = models.CharField(choices=TaskPriority.choices, default=TaskPriority.MEDIUM)
    status = models.CharField(choices=TaskStatus.choices, default=TaskStatus.NEW)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    performers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="related_tasks",
    )
