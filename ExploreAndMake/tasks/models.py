from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    position = models.CharField(max_length=100, blank=True, help_text='Должность')

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return f"{self.username} ({self.email})"

class Project(models.Model):
    title = models.CharField(max_length=64, db_index=True)
    description = models.TextField(blank=True, help_text="Описание")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_projects',
    )

    class Meta:
        db_table = 'projects'
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['owner', '-created_at']),
        ]

    def __str__(self):
        return self.title

    def is_member(self, user):
        return self.memberships.filter(user=user).exists()

class ProjectMembership(models.Model):

    class RoleChoices(models.TextChoices):
        OWNER = 'owner', 'Владелец'
        MEMBER = 'member', 'Участник'
        VIEWER = 'viewer', 'Наблюдатель'

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_memberships'
    )
    role = models.CharField(
        max_length=10,
        choices=RoleChoices.choices,
        default=RoleChoices.MEMBER
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'project_memberships'
        verbose_name = 'Участник проекта'
        verbose_name_plural = 'Участники проектов'
        constraints = [
            models.UniqueConstraint(fields=['project', 'user'], name='unique_project_user')
        ]
        indexes = [models.Index(fields=['user', 'role'])]

    def __str__(self):
        return f"{self.user.username} -> {self.project.title} {self.role}"

class Task(models.Model):
    class PriorityChoices(models.IntegerChoices):
        LOW = 1, 'Низкий'
        MEDIUM = 2, 'Средний'
        HIGH = 3, 'Высокий'
        URGENT = 4, 'Критический'

    class StatusChoices(models.TextChoices):
        BACKLOG = 'backlog', 'Бэклог'
        TODO = 'todo', 'К выполнению'
        IN_PROGRESS = 'in_progress', 'В работе'
        REVIEW = 'review', 'На проверке'
        DONE = 'done', 'Готово'
        CANCELLED = 'cancelled', 'Отменено'

    title = models.CharField(max_length=64, db_index=True)
    description = models.TextField(blank=True, help_text='Описание')

    priority = models.IntegerField(choices=PriorityChoices.choices,
    default=PriorityChoices.MEDIUM,
    db_index=True
    )

    status = models.CharField(choices=StatusChoices.choices,
    default=StatusChoices.TODO,
    db_index=True
    )

    deadline = models.DateTimeField(null=True,
    blank=True,
    db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )
    asign = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )

    class Meta:
        db_table = 'tasks'
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-priority', 'deadline', '-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['asign', 'status']),
            models.Index(fields=['deadline']),
        ]

    def __str__(self):
        return f"[{self.get_priority_display()}] {self.title}"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.deadline and self.deadline < timezone.now():
            raise ValidationError({'deadline': "Дедлайн не может быть в прошлом."})

        if self.asign and not self.project.is_member(self.asign):
            raise ValidationError({'asign': "Исполнитель должен быть участником проекта."})

