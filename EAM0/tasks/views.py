from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Task, Project
from .serializers import TaskSerializer, ProjectSerializer, UserSerializer
from .permissions import TaskPermission

User = get_user_model()


@extend_schema(
    summary="Управление задачами проекта",
    description="CRUD-операции над задачами с матрицей ролевого доступа.",
    tags=["Tasks"],
)
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, TaskPermission]
    filter_backends = [DjangoFilterBackend]
    
    filterset_fields = {
        "project": ["exact"],
        "status": ["exact"],
        "priority": ["exact"],
        "performer": ["exact", "isnull"],
        "deadline": ["exact", "gte", "lte"],
    }

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Task.objects.none()

        return Task.objects.filter(
            Q(project__participants=user) | Q(project__owner=user)
        ).distinct().select_related(
            "project", "author", "performer"
        ).prefetch_related(
            "project__participants"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


@extend_schema(
    summary="Список проектов",
    description="Возвращает проекты, участником которых является текущий пользователь.",
    tags=["Projects"],
)
class ProjectListViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(
            Q(participants=user) | Q(owner=user)
        ).distinct().order_by('name')


@extend_schema(
    summary="Список пользователей",
    description="Возвращает список всех пользователей (для выбора исполнителя).",
    tags=["Users"],
)
class UserListViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all().order_by('first_name', 'last_name')