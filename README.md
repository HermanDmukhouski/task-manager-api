# task-manager-api

Backend-сервис для учёта задач пользователей (FastAPI + PostgreSQL, async SQLAlchemy 2.0).

Сервис позволяет:

1. Создавать пользователя.
2. Создавать задачу для пользователя.
3. Получать список задач пользователя (фильтр по статусу + курсорная пагинация).
4. Обновлять статус задачи.
5. Удалять задачу.
6. Получать статистику по задачам пользователя.

## Быстрый старт (Docker)

```bash
docker compose up --build
```

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Локальный запуск (без Docker)

Требуется Python 3.11+ и Poetry.

```bash
cp .env.example .env
make install            # poetry install + pre-commit hooks
docker compose up -d postgres
make migrate            # alembic upgrade head
make dev                # uvicorn с autoreload
```

## Тесты

Тесты разделены на unit (без БД), integration (репозитории/UoW на реальной БД)
и e2e (HTTP через ASGI-клиент). Integration/e2e ожидают PostgreSQL на
`localhost:5432` с базой `task_manager_test`:

```bash
docker compose up -d postgres
docker exec task_manager_postgres psql -U postgres -c "CREATE DATABASE task_manager_test" || true
make test               # poetry run pytest
```

Только unit-тесты (БД не нужна):

```bash
poetry run pytest tests/unit
```

Линтеры и типизация:

```bash
make lint               # ruff
make typecheck          # mypy --strict
make check              # lint + typecheck + test
```

## Архитектура

Слоистая архитектура (clean architecture + CQRS):

```
src/
  domain/           # агрегаты (User, Task), value objects, доменные события, инварианты
  application/      # команды/запросы и их хендлеры, интерфейсы репозиториев и UnitOfWork
  infrastructure/   # async SQLAlchemy: модели, репозитории, UoW, DI-контейнер (dishka)
  interfaces/       # FastAPI: роутеры, pydantic-схемы, exception handlers, middleware
```

- Зависимости направлены внутрь: `interfaces -> application -> domain`,
  `infrastructure` реализует интерфейсы application-слоя.
- Бизнес-правила (валидация title/name/email, допустимые переходы статусов)
  живут в домене; доменные ошибки маппятся на HTTP-коды в exception handlers.
- Запись идёт через агрегаты и UnitOfWork, чтение — через query-хендлеры.

## API

| Метод  | Путь                           | Описание                        | Коды ошибок |
| ------ | ------------------------------ | ------------------------------- | ----------- |
| POST   | `/users`                       | Создать пользователя            | 409, 422    |
| GET    | `/users/{user_id}`             | Получить пользователя           | 404         |
| POST   | `/users/{user_id}/tasks`       | Создать задачу                  | 404, 422    |
| GET    | `/users/{user_id}/tasks`       | Список задач (фильтр/пагинация) | 404, 422    |
| PATCH  | `/tasks/{task_id}/status`      | Обновить статус задачи          | 404, 422    |
| DELETE | `/tasks/{task_id}`             | Удалить задачу                  | 404         |
| GET    | `/users/{user_id}/tasks/stats` | Статистика по задачам           | 404         |

Статусы задачи: `new` (по умолчанию), `in_progress`, `done`, `cancelled`.
Допустимые переходы: `new -> in_progress | cancelled`,
`in_progress -> done | cancelled | new`; `done` и `cancelled` — терминальные.

### Примеры запросов

Создать пользователя:

```bash
curl -X POST http://localhost:8000/users \
  -H 'Content-Type: application/json' \
  -d '{"email": "user@example.com", "name": "Ivan"}'
# 201 {"id": 1, "email": "user@example.com", "name": "Ivan", "created_at": "..."}
```

Получить пользователя:

```bash
curl http://localhost:8000/users/1            # 200, либо 404 если не найден
```

Создать задачу:

```bash
curl -X POST http://localhost:8000/users/1/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title": "Подготовить отчет", "description": "Собрать данные за неделю"}'
# 201 {"id": 1, "user_id": 1, "title": "...", "status": "new", ...}
```

Список задач с фильтром и пагинацией:

```bash
curl 'http://localhost:8000/users/1/tasks?status=new&limit=2'
# 200 {"items": [...], "next_cursor": "eyJjcmVhdGVkX2F0IjogIi4uLiJ9"}

curl 'http://localhost:8000/users/1/tasks?limit=2&cursor=eyJjcmVhdGVkX2F0IjogIi4uLiJ9'
# следующая страница; next_cursor == null на последней странице
```

> Вместо `limit/offset` используется keyset-пагинация (cursor-based):
> `next_cursor` — непрозрачный токен позиции `(created_at, id)` последнего
> элемента. Это стабильно при вставках между запросами и не деградирует на
> больших смещениях; запрос покрыт составным индексом `(user_id, created_at, id)`.

Обновить статус задачи:

```bash
curl -X PATCH http://localhost:8000/tasks/1/status \
  -H 'Content-Type: application/json' \
  -d '{"status": "in_progress"}'
# 200; 404 если нет задачи; 422 при неизвестном статусе или недопустимом переходе
```

Удалить задачу:

```bash
curl -X DELETE http://localhost:8000/tasks/1 -i
# 204 No Content; 404 если задачи нет
```

Статистика:

```bash
curl http://localhost:8000/users/1/tasks/stats
# 200 {"total": 10, "new": 3, "in_progress": 2, "done": 4, "cancelled": 1}
```

## Миграции

```bash
make migrate                            # alembic upgrade head
make makemigrations msg="add field"     # autogenerate новой ревизии
```

В Docker миграции применяются автоматически при старте контейнера API.

## Стек

- Python 3.11+, FastAPI, Uvicorn
- PostgreSQL, async SQLAlchemy 2.0, asyncpg, Alembic
- Pydantic v2, pydantic-settings
- Dishka (DI), Pytest, Ruff, Mypy (strict), pre-commit
- Docker / Docker Compose, GitHub Actions
