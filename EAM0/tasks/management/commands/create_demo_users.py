from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tasks.models import Project, Task, TaskPriority, TaskStatus
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Создает 5 демо-пользователей согласно ТЗ: Иван, Мария, Алексей, Ольга, Admin'

    def handle(self, *args, **options):
        # Данные пользователей из ТЗ
        users_data = [
            {
                'username': 'ivan',
                'email': 'ivan@alpha-soft.ru',
                'password': 'ivan123',
                'first_name': 'Иван',
                'last_name': 'Петров',
                'position': 'Tech Lead',
                'phone': '+7 (999) 111-22-33',
                'is_superuser': False,
            },
            {
                'username': 'maria',
                'email': 'maria@alpha-soft.ru',
                'password': 'maria123',
                'first_name': 'Мария',
                'last_name': 'Сидорова',
                'position': 'Senior Developer',
                'phone': '+7 (999) 222-33-44',
                'is_superuser': False,
            },
            {
                'username': 'alexey',
                'email': 'alexey@alpha-soft.ru',
                'password': 'alexey123',
                'first_name': 'Алексей',
                'last_name': 'Иванов',
                'position': 'Junior Developer',
                'phone': '+7 (999) 333-44-55',
                'is_superuser': False,
            },
            {
                'username': 'olga',
                'email': 'olga@alpha-soft.ru',
                'password': 'olga123',
                'first_name': 'Ольга',
                'last_name': 'Смирнова',
                'position': 'Project Manager',
                'phone': '+7 (999) 444-55-66',
                'is_superuser': False,
            },
            {
                'username': 'admin',
                'email': 'admin@alpha-soft.ru',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': '',
                'position': 'System Administrator',
                'phone': '',
                'is_superuser': True,
                'is_staff': True,
            },
        ]

        created_users = []
        for user_data in users_data:
            # ✅ ИСПРАВЛЕНИЕ: сохраняем username, но не удаляем из словаря
            username = user_data['username']
            password = user_data['password']  # ✅ Сохраняем пароль для вывода
            position = user_data['position']  # ✅ Сохраняем позицию для вывода
            
            # Создаем копию данных без пароля для create_user
            user_fields = {k: v for k, v in user_data.items() if k != 'password'}
            
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'Пользователь {username} уже существует, пропускаем...')
                )
                user = User.objects.get(username=username)
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,  # ✅ Передаем пароль отдельно
                    **user_fields
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Создан пользователь: {username} ({user.position})')
                )
            
            created_users.append({
                'user': user,
                'username': username,
                'password': password,
                'position': position,
            })

        # Создадим демо-проект и задачи для тестирования
        self._create_demo_data()

        self.stdout.write(self.style.SUCCESS('\n🎉 Готово! Все пользователи созданы.'))
        self.stdout.write(self.style.SUCCESS('\n📋 Данные для входа:'))
        self.stdout.write(self.style.SUCCESS('┌─────────────┬──────────────┬──────────────────────┐'))
        self.stdout.write(self.style.SUCCESS('│ Логин       │ Пароль       │ Роль                 │'))
        self.stdout.write(self.style.SUCCESS('├─────────────┼──────────────┼──────────────────────┤'))
        
        # ✅ ИСПРАВЛЕНИЕ: используем created_users вместо users_data
        for user_info in created_users:
            self.stdout.write(self.style.SUCCESS(
                f"│ {user_info['username']:<11} │ {user_info['password']:<12} │ {user_info['position']:<20} │"
            ))
        
        self.stdout.write(self.style.SUCCESS('└─────────────┴──────────────┴──────────────────────┘'))

    def _create_demo_data(self):
        """Создает демо-проект и задачи для тестирования"""
        # Получаем пользователей
        try:
            ivan = User.objects.get(username='ivan')
            maria = User.objects.get(username='maria')
            alexey = User.objects.get(username='alexey')
            olga = User.objects.get(username='olga')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Не все пользователи созданы. Запустите команду заново.'))
            return

        # Создаем проект
        project, created = Project.objects.get_or_create(
            name='Alpha-Soft CRM',
            defaults={
                'description': 'Разработка внутренней CRM-системы для управления клиентами',
                'owner': olga,
            }
        )
        
        if created:
            project.participants.set([ivan, maria, alexey, olga])
            self.stdout.write(self.style.SUCCESS(f'\n📁 Создан проект: {project.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'\n📁 Проект {project.name} уже существует'))

        # Создаем демо-задачи
        tasks_data = [
            {
                'title': 'Разработать архитектуру базы данных',
                'description': 'Спроектировать схему БД для модулей клиентов, заказов и отчетности',
                'priority': TaskPriority.CRITICAL,
                'status': TaskStatus.DONE,
                'deadline': timezone.now() - timedelta(days=5),
                'author': ivan,
                'performer': ivan,
            },
            {
                'title': 'Реализовать REST API для клиентов',
                'description': 'Создать endpoints: GET /clients, POST /clients, PUT /clients/<id>, DELETE /clients/<id>',
                'priority': TaskPriority.HIGH,
                'status': TaskStatus.IN_PROGRESS,
                'deadline': timezone.now() + timedelta(days=3),
                'author': olga,
                'performer': maria,
            },
            {
                'title': 'Настроить JWT аутентификацию',
                'description': 'Интегрировать djangorestframework-simplejwt, настроить refresh/access токены',
                'priority': TaskPriority.HIGH,
                'status': TaskStatus.IN_REVIEW,
                'deadline': timezone.now() + timedelta(days=1),
                'author': olga,
                'performer': ivan,
            },
            {
                'title': 'Написать unit-тесты для serializers',
                'description': 'Покрыть тестами TaskSerializer и ProjectSerializer, минимум 80% coverage',
                'priority': TaskPriority.MEDIUM,
                'status': TaskStatus.NEW,
                'deadline': timezone.now() + timedelta(days=7),
                'author': maria,
                'performer': alexey,
            },
            {
                'title': 'Подготовить документацию API',
                'description': 'Настроить drf-spectacular, добавить docstrings ко всем ViewSet',
                'priority': TaskPriority.MEDIUM,
                'status': TaskStatus.NEW,
                'deadline': timezone.now() + timedelta(days=10),
                'author': olga,
                'performer': None,  # Не назначена
            },
            {
                'title': 'Исправить баг в фильтрации задач',
                'description': 'При фильтрации по deadline__gte возвращается неверный результат',
                'priority': TaskPriority.LOW,
                'status': TaskStatus.CANCELLED,
                'deadline': None,
                'author': ivan,
                'performer': alexey,
            },
        ]

        created_count = 0
        for task_data in tasks_data:
            task, created = Task.objects.get_or_create(
                title=task_data['title'],
                project=project,
                defaults=task_data
            )
            if created:
                created_count += 1

        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f'✅ Создано {created_count} демо-задач в проекте'))