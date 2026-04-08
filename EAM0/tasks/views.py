from django.shortcuts import render, get_object_or_404

from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        serializer.save(performer=self.request.user)

    def create(self, request):
        project_id = request.data.get('project')
        project = get_object_or_404(Project, id=project_id)

        if not project_id:
            return Response(
                {"detail": "Поле 'project' обязательно!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user not in project.participants.all():
            return Response(
                {"detail": "У вас нет доступа к этому проекту"},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().create(request)

    def update(self, request):
        task = self.get_object()
        
        if task.project.owner != request.user:
            return Response(
                {"detail": "Только владелец проекта может редактировать задачи"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request)
    
    def destroy(self, request):
        task = self.get_object()
        
        if task.project.owner != request.user:
            return Response(
                {"detail": "Только владелец проекта может удалить задачу"},
                status=stauts.HTTP_403_FORBIDDEN
            )
    
    def partial_update(self, request):
        task = self.get_object()
        user = request.user

        requested_fields = set(request.data.keys())
        ignored_fields = {'id', 'created_at', 'updated_at', 'project', 'author'}
        fields_to_check = requested_fields - ignored_fields

        if task.project.owner == user:
            allowed_fields = {'title', 'description', 'status', 'priority', 'deadline', 'performer'}
        elif task.performer == user:
            allowed_fields = {'status', 'priority'}
        elif task.author == user:
            allowed_fields = {'description'}
        else:
            return Response(
                {"detail": "Недостаточно прав для редактирования этой задачи"},
                status=status.HTTP_403_FORBIDDEN
            )

        forbidden_fields = fields_to_check - allowed_fields
        if forbidden_fields:
            return Response(
                {"detail": f"Нельзя изменять поля: {', '.join(forbidden_fields)}"},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().partial_update(request)
