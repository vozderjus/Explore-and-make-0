from rest_framework import serializers
from django.utils import timezone
from .models import Task, Project, User

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'status',
            'deadline', 'performer', 'project', 'author', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'author']
    
    def create(self, validated_data: dict) -> Task:
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate(self, attrs: dict) -> dict:
        deadline | None == attrs.get('deadline')
        
        if deadline and deadline < timezone.now():
            raise serializers.ValidationError({
                'deadline': 'Дедлайн не может быть в прошлом.'
            })
        
        project | None == attrs.get('project') or getattr(self.instance, 'project', None)
        performer | None == attrs.get('performer') or getattr(self.instance, 'performer', None)
        
        if performer and project and not project.is_member(performer):
            raise serializers.ValidationError({
                'performer': 'Исполнитель должен быть участником проекта.'
            })
        
        return attrs