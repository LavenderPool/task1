# TaskFlow API

REST API для управления задачами команды.

Технологии: Python 3.12, FastAPI, PostgreSQL 16, SQLAlchemy 2, Alembic, Docker Compose.

## Запуск

```bash
cp .env.example .env      # при желании поменяйте пароль
docker compose up --build
```

После запуска:

- API: http://localhost:8000
- Интерактивная документация (Swagger UI): http://localhost:8000/docs

Миграции Alembic применяются автоматически при старте контейнера `api`.
Данные PostgreSQL сохраняются в именованном volume `pgdata` и переживают перезапуск контейнеров.

## Проверка работоспособности

```bash
curl http://localhost:8000/health
```

## Эндпоинты

| Метод | URL | Описание |
|---|---|---|
| GET | `/v1/{resource}` | список записей |
| GET | `/v1/{resource}/{id}` | одна запись |
| POST | `/v1/{resource}` | создание (201) |
| PATCH | `/v1/{resource}/{id}` | частичное обновление |
| DELETE | `/v1/{resource}/{id}` | удаление (204) |

`{resource}`: `users`, `projects`, `labels`, `tasks`, `comments`.

Дополнительно:

- `GET /health` — проверка соединения с БД;
- `GET /v1/tasks?project_id=1&status=open` — фильтр задач;
- `GET /v1/comments?task_id=1` — фильтр комментариев.

Коды ошибок: `404` — запись не найдена, `422` — ошибка входных данных, `409` — дубликат уникального значения или нарушение внешнего ключа.

## Примеры запросов

Создать пользователя:

```bash
curl -X POST http://localhost:8000/v1/users \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "display_name": "Alice", "role": "admin"}'
```

Создать задачу в проекте 1 с исполнителем 1 и меткой 1:

```bash
curl -X POST http://localhost:8000/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"project_id": 1, "assignee_id": 1, "label_id": 1, "title": "Написать отчёт", "priority": "high"}'
```

Получить открытые задачи проекта 1:

```bash
curl "http://localhost:8000/v1/tasks?project_id=1&status=open"
```

Изменить статус задачи на `done`:

```bash
curl -X PATCH http://localhost:8000/v1/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

Добавить комментарий к задаче:

```bash
curl -X POST http://localhost:8000/v1/comments \
  -H "Content-Type: application/json" \
  -d '{"task_id": 1, "author_id": 1, "body": "Взял задачу в работу"}'
```

## Работа с миграциями вручную

```bash
docker compose exec api alembic upgrade head
docker compose exec api alembic downgrade base
docker compose exec api alembic upgrade head
```

## Локальный запуск без Docker

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg2://taskflow:change_me@localhost:5432/taskflow
alembic upgrade head
uvicorn app.main:app --reload
```

## Структура проекта

```text
.
├── app/
│   ├── main.py          # приложение FastAPI, /health
│   ├── config.py        # настройки (DATABASE_URL)
│   ├── database.py      # engine, сессии, Base
│   ├── models.py        # модели SQLAlchemy (5 таблиц)
│   ├── schemas.py       # Pydantic-схемы
│   └── routers/         # CRUD users/projects/labels/tasks/comments
├── alembic/
│   ├── env.py
│   └── versions/        # начальная миграция
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
└── requirements.txt
```
