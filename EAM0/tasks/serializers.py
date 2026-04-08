from rest_framework import serializers

from .models import Project, Task, TaskStatus, TaskPriority

class ProjectSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Project
        fields = ('name', 'description', 'owner', 'participants')
        read_only_fields = ['owner', 'participants']
    
    def create(self, validated_data):
        validated_data.pop('owner', None)
        validated_data.pop('participants', None)
        
        request = self.context.get('request')
        user = request.user
        
        project = Projects.objects.create(owner=user, **validated_data)
        
        project.participants.add(user)
        
        return project
        

class TaskSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Task
        fields = ('id',
                  'project',
                  'title',
                  'description', 
                  'priority',
                  'status',
                  'created_at',
                  'updated_at',
                  'author',
                  'performer',
                  'deadline',
        )
    
    def validate(self, data):
        performer = data.get('performer')
        project = data.get('project')
        
        if not project and hasattr(self, 'instance') and self.instance:
            project = self.instance.project

        if not performer:
            return data
        
        if not project:
            raise serializers.ValidationError({'project': "Проект обязателен"})
        
        if not project.participants.filter(id=performer.id).exists():
            raise serializers.ValidationError('Исполнитель должен быть участником проекта')
        
        return data
    
    