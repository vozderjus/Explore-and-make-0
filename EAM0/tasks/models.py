from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class TaskPriority(models.IntegerChoices):
    LOW = 1, 'Низкий'
    MEDIUM = 2, 'Средний'
    HIGH = 3, 'Высокий'
    CRITICAL = 4, 'Критический'


class TaskStatus(models.TextChoices):
    NEW = 'new', 'Новая'
    IN_PROGRESS = 'in_progress', 'В работе'
    IN_REVIEW = 'in_review', 'На проверке'
    DONE = 'done', 'Выполнена'
    CANCELLED = 'cancelled', 'Отменена'

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    position = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email']

class Project(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="project_memberships",
    )
    
    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-updated_at', 'name']
        indexes = [
            models.Index(fields=['owner', '-created_at'])
        ]
    
    def is_member(self, user):
        return self.participants.filter(pk=user.pk).exists()


class Task(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)

    priority = models.IntegerField(
        choices=TaskPriority.choices,
        default=TaskPriority.MEDIUM,
        db_index=True
        )

    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.NEW,
        db_index=True
        )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    deadline = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tasks",
    )
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    performer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
        blank=True,
        null=True
    )

    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.deadline and self.deadline < timezone.now():
            raise ValidationError({'deadline': "Дедлайн не может быть в прошлом."})
        
        if self.performer and not self.project.is_member(self.performer):
            raise ValidationError({'performer': "Исполнитель должен быть участником проекта."})
    
    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = [
            '-priority',
            'deadline',
            '-created_at'
        ]
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['project', 'priority']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['deadline']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
        ]