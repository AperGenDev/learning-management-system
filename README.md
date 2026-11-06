# learning-management-system

Система управления учебными курсами 

Апергенов Дамир, Богданов Данил

## Состояние: ЛР3 (gRPC)

| Компонент | Технологии | Как запускается |
|---|---|---|
| PostgreSQL | PostgreSQL 15 | Docker |
| API Service | FastAPI, SQLAlchemy, Pydantic, JWT | процесс на компьютере, порт 8000 |
| Recommendation Service | gRPC, Protocol Buffers | процесс на компьютере, порт 50051 |


## Структура

```
backend/                 API Service (FastAPI)
  api/                   роутеры REST API
  services/              бизнес-логика
  schemas/               Pydantic-модели запросов и ответов (DTO)
  models.py, crud.py     модели SQLAlchemy и операции с БД (ЛР1)
  recommendation_client.py  gRPC-клиент
grpc_contracts/          .proto-контракт и сгенерированный код
recommendation_service/  gRPC-сервис рекомендаций
migrations/              миграции Alembic
```

## Запуск (Windows, PowerShell)

Нужны: Python 3.11+, Docker Desktop. Все команды выполняются **из корня проекта**.

### Один раз
```
docker compose up -d                 # PostgreSQL на порту 5433
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m grpc_contracts.generate    # сгенерировать код из .proto под вашу версию grpcio
alembic upgrade head                 # создать таблицы
python -m backend.seed_data          # тестовые данные
```

> Если раньше база создавалась через `create_tables.py`, сначала выполните
> `docker compose down -v` (удалит старую базу), потом команды выше.

### Каждый раз — два терминала
```
# терминал 1
venv\Scripts\activate
python -m recommendation_service.server

# терминал 2
venv\Scripts\activate
uvicorn backend.main:app --reload
```

Swagger: http://localhost:8000/docs → **Authorize** → `student@example.com` / `student123`.

### Тестовые пользователи

| Email | Пароль | Роль |
|---|---|---|
| student@example.com | student123 | студент |
| student2@example.com | student123 | студент |
| teacher@example.com | teacher123 | преподаватель |
| admin@example.com | admin123 | администратор |

### Полезные команды
```
python -m backend.test_scenarios     # ЛР1: сценарии работы с БД в консоли
alembic downgrade base               # удалить все таблицы
alembic upgrade head                 # создать заново
```
