# task-manager-api

Backend-сервис для учёта задач пользователей (FastAPI + PostgreSQL, async SQLAlchemy).

## Задача

Сервис позволяет:

1. Создавать пользователя.
2. Создавать задачу для пользователя.
3. Получать список задач пользователя (с фильтрацией по статусу и пагинацией).
4. Обновлять статус задачи.
5. Удалять задачу.
6. Получать статистику по задачам пользователя.

## Сущности

### User
- `id`
- `email` — уникальный, валидируемый
- `name` — непустой
- `created_at`

### Task
- `id`
- `user_id`
- `title` — обязателен
- `description` — опционален
- `status` — `new` / `in_progress` / `done` / `cancelled` (по умолчанию `new`)
- `created_at`
- `updated_at`

## API

| Метод  | Путь                              | Описание                       |
| ------ | --------------------------------- | ------------------------------ |
| POST   | `/users`                          | Создать пользователя           |
| GET    | `/users/{user_id}`                | Получить пользователя          |
| POST   | `/users/{user_id}/tasks`          | Создать задачу                 |
| GET    | `/users/{user_id}/tasks`          | Список задач (фильтр/пагинация)|
| PATCH  | `/tasks/{task_id}/status`         | Обновить статус задачи         |
| DELETE | `/tasks/{task_id}`                | Удалить задачу                 |
| GET    | `/users/{user_id}/tasks/stats`    | Статистика по задачам          |

## Стек

- Python 3.11+
- FastAPI / Uvicorn
- PostgreSQL + async SQLAlchemy 2.0 + asyncpg
- Pydantic v2 / pydantic-settings
- Alembic
- Dishka (DI)
- Pytest / Ruff / Mypy / pre-commit
- Docker / Docker Compose

## Архитектура

```
src/
  domain/          # сущности, value objects, доменные интерфейсы, события, исключения
  application/      # команды, запросы, хендлеры, абстракции (UnitOfWork)
  infrastructure/   # SQLAlchemy, репозитории, DI-контейнер, диспетчер событий
  interfaces/       # FastAPI роутеры, схемы, middleware, DI для эндпоинтов
```
