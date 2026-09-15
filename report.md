# Отчёт по домашней работе №2
## Взаимодействие с источниками данных (ML + PostgreSQL)

## 1. Артефакты

- **GitHub:** https://github.com/1rizhik/devops_hw2
- **Docker Hub:** https://hub.docker.com/r/1rizhik/devops_hw2
- **Образ:** `1rizhik/devops_hw2:latest`
- **База:** форк `devops_hw1` (BankNote Authentication)

## 2. Вариант задания — C

Модель **читает** признаки из БД и **пишет** результат обратно:

Client → POST /predict {request_id} → API
↓
SELECT features FROM requests WHERE id = request_id
↓
model.predict(features)
↓
INSERT INTO predictions


## 3. База данных

PostgreSQL 16 в Docker. Две таблицы:
- **`requests`** — `id`, `features` (JSONB), `created_at`
- **`predictions`** — `id`, `request_id` (FK), `prediction`, `created_at`

Тестовые данные (3 записи BankNote) загружаются из `db/init.sql` при первом старте.

## 4. API-сервис

Flask (`src/app.py`):

- `GET /health` — `{"status": "ok"}`
- `POST /predict` — `{"request_id": N}` → читает из БД, предсказывает, пишет в БД
- `GET /predictions/<id>` — история предсказаний

## 5. Безопасность

Пароли БД не хардкодятся — через `.env` (не в Git). В `docker-compose.yml` — переменные `${POSTGRES_USER}` и т.д.

## 6. Docker Compose

- `db` — PostgreSQL, порт 5432, healthcheck, `db/init.sql`
- `ml-api` — Flask API, порт 5000, `depends_on: db`

## 7. Тесты

`tests/test_api.py` — 6 тестов с реальной БД: health, predict (0 и 1), 400, 404, история.

## 8. CI Pipeline

`.github/workflows/ci.yml`:
- Job `test` — сервис-контейнер PostgreSQL 16, `pytest`
- Job `build-and-push` (push в main) — сборка и push образа

## 9. CD Pipeline

`.github/workflows/cd.yml` — после успешного CI:
- `docker compose up -d --build` — полный стек
- `run_scenario.py` — 5 сценариев
- Проверка `SELECT * FROM predictions`

**Результат:** все сценарии пройдены, записи в БД присутствуют.

## 10. Выводы

Реализовано взаимодействие ML-модели с PostgreSQL по варианту C. Пароли БД — только через переменные окружения. CI/CD запускают полный стек с проверкой БД.

Все требования задания выполнены.