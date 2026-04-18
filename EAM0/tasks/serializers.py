from rest_framework import serializers
from django.utils import timezone
from .models import Task, Project, User


class UserShortSerializer(serializers.ModelSerializer):
    """Краткая информация о пользователе"""
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        full_name = f"{instance.first_name} {instance.last_name}".strip()
        data['display_name'] = full_name if full_name else instance.email
        return data


class ProjectShortSerializer(serializers.ModelSerializer):
    """Краткая информация о проекте"""
    class Meta:
        model = Project
        fields = ['id', 'name']


class TaskSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)
    performer = UserShortSerializer(read_only=True)
    project = ProjectShortSerializer(read_only=True)
    
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.none(),
        source='author',
        write_only=True,
        required=False
    )
    performer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='performer',
        write_only=True,
        required=False,
        allow_null=True
    )
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        source='project',
        write_only=True,
        required=False
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'status',
            'deadline', 'performer', 'performer_id', 'project', 'project_id',
            'author', 'author_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'author']

    def create(self, validated_data):
        # Автор подставляется автоматически
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        # Валидация дедлайна
        deadline = attrs.get('deadline')
        if deadline and deadline < timezone.now():
            raise serializers.ValidationError({
                'deadline': 'Дедлайн не может быть в прошлом.'
            })

        # Валидация исполнителя
        project = attrs.get('project') or getattr(self.instance, 'project', None)
        performer = attrs.get('performer') or getattr(self.instance, 'performer', None)

        if performer and project:
            if not project.participants.filter(pk=performer.pk).exists():
                raise serializers.ValidationError({
                    'performer': 'Исполнитель должен быть участником проекта.'
                })

        return attrs