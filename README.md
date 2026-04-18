# Alpha-Soft Task Tracker
Внутренний таск-трекер для dev-компании с ролевым доступом, Kanban-доской и REST API на Django + DRF.

## 📦 Быстрый старт
```bash
# 1. Клонирование и окружение
git clone <repo_url> && cd task-tracker
python -m venv venv && source venv/bin/activate  # Win: venv\Scripts\activate

# 2. Установка зависимостей
pip install -r requirements.txt

# 3. Миграции и демо-данные
python manage.py migrate
python manage.py create_demo_users

# 4. Запуск сервера
python manage.py runserver
```

## 🌐 Доступные эндпоинты
| Сервис | URL |
|--------|-----|
| 🖥️ Kanban Frontend | http://127.0.0.1:8000/ |
| 🔗 REST API | http://127.0.0.1:8000/api/ |
| 📖 Swagger UI | http://127.0.0.1:8000/api/schema/swagger-ui/ |
| 📄 ReDoc | http://127.0.0.1:8000/api/schema/redoc/ |

## 🔑 Тестовые учетные записи
| Логин | Пароль | Роль | Права в задачах |
|-------|--------|------|-----------------|
| `olga` | `olga123` | Project Manager | Создание проектов/задач |
| `ivan` | `ivan123` | Tech Lead (Owner) | Полный доступ к своим задачам |
| `maria` | `maria123` | Senior Developer | Автор/Исполнитель |
| `alexey` | `alexey123` | Junior Developer | Только статус/приоритет |
| `admin` | `admin123` | Superuser | Полный доступ к системе |

## 🧪 Примеры запросов (cURL)
```bash
# 1. Получить JWT токен
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"olga","password":"olga123"}'

# 2. Создать задачу (автор подставляется автоматически)
export TOKEN="<ваш_access_token>"
curl -X POST http://127.0.0.1:8000/api/tasks/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Фикс бага в авторизации","project_id":1,"priority":3}'

# 3. Фильтрация задач (в работе, дедлайн до конца месяца)
curl "http://127.0.0.1:8000/api/tasks/?status=in_progress&deadline__lte=2026-04-30T23:59:59" \
  -H "Authorization: Bearer $TOKEN"
```

## 🏗 Архитектура прав
| Роль | CRUD задач | Ограничения полей |
|------|------------|-------------------|
| **Owner** | ✅ Все операции | Без ограничений |
| **Author** | ✅ Read / Update / Delete | Только `description` |
| **Performer** | ✅ Read / Update | Только `status`, `priority` |
| **Participant** | ✅ Read only | ❌ Редактирование/удаление |
| **Non-member** | ❌ Полный отказ | Возврат `404` |

> 💡 Все операции защищены на уровне `get_queryset()` и кастомных `BasePermission`. Прямой подбор ID чужих задач невозможен. Валидация бизнес-правил дублируется в сериализаторах и моделях (`clean()` ↔ `validate()`).

## 📝 Лицензия
MIT © 2026 Alpha-Soft
