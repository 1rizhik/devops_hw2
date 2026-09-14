# Отчёт по домашней работе №2
## Взаимодействие с источниками данных (ML + PostgreSQL)

## 1. Ссылки на артефакты

- **GitHub репозиторий:** https://github.com/1rizhik/devops_hw2
- **Docker Hub:** https://hub.docker.com/r/1rizhik/devops_hw2
- **Ветки:** `main` (release), `develop` (разработка)
- **Образ:** `1rizhik/devops_hw2:latest`
- **Базовый репозиторий:** форк `devops_hw1` (BankNote Authentication)

## 2. Вариант задания

**Вариант C:** модель **читает** входные данные из БД и **записывает** результат обратной связи.

Архитектура:
Client → POST /predict {request_id} → Flask API
↓

SELECT features FROM requests WHERE id = request_id
↓

model.predict(features)
↓

INSERT INTO predictions (request_id, prediction)
↓
← JSON {request_id, prediction, prediction_id}


## 3. Набор данных

**BankNote Authentication** (UCI ML Repository, dataset 267):
- 1372 образца, 4 признака (variance, skewness, curtosis, entropy)
- Целевая переменная: `class` (0 — подлинная, 1 — поддельная)
- Разделение: 80% train (1097), 20% test (275)

## 4. Модель

- **RandomForestClassifier** (n_estimators=100, random_state=42)
- Метрики на тесте:
  - **Accuracy: 0.9964**
  - **F1: 0.9959**
  - **Precision: 0.9919**
  - **Recall: 1.0000**

## 5. API-сервис

Flask-приложение (`src/app.py`):

| Эндпоинт | Метод | Описание |
|---|---|---|
| `/health` | GET | `{"status": "ok"}` |
| `/predict` | POST | `{"request_id": 1}` → читает из БД, предсказывает, записывает |
| `/predictions/<id>` | GET | История предсказаний по request_id |

**Пример ответа `/predict`:**
```json
{
  "request_id": 1,
  "prediction": 0,
  "prediction_id": 1
}

6. База данных
PostgreSQL 16-alpine (в Docker-контейнере).

Схема (db/init.sql):

requests — входные признаки

id SERIAL PRIMARY KEY

features JSONB NOT NULL

created_at TIMESTAMP

predictions — результаты предсказаний

id SERIAL PRIMARY KEY

request_id INTEGER REFERENCES requests(id)

prediction INTEGER

created_at TIMESTAMP

Тестовые данные (3 записи BankNote) загружаются автоматически при первом старте контейнера.

7. Аутентификация и безопасность
Пароли БД не хардкодятся — передаются через переменные окружения

.env — локально, не коммитится в Git (в .gitignore)

.env.example — шаблон для документации

В docker-compose.yml — ${POSTGRES_USER}, ${POSTGRES_PASSWORD} из .env

В GitHub Actions CD — .env создаётся на лету из литеральных значений (без секретов)

8. Docker Compose
docker-compose.yml описывает 2 сервиса:

db — PostgreSQL, порт 5432, healthcheck, volume db_data, монтирует db/init.sql

ml-api — Flask API, порт 5000, depends_on: db (service_healthy), env-переменные БД

Запуск:

bash
docker compose up -d --build

9. Тесты
tests/test_api.py — 6 тестов с реальной БД:

test_health — health-check

test_predict_authentic — request_id=1 → prediction=0

test_predict_fake — request_id=2 → prediction=1

test_predict_missing_request_id — 400

test_predict_not_found — 404

test_predictions_history — история по request_id

tests/conftest.py — добавляет корень проекта в sys.path

10. CI Pipeline (GitHub Actions)
Файл: .github/workflows/ci.yml

Триггеры:

pull_request в main → job test

push в main → jobs test + build-and-push

Job test:

Сервис-контейнер PostgreSQL 16 (services: postgres)

Python 3.12

Установка зависимостей

Initialize database schema — psql -f db/init.sql

pytest tests/ -v

Job build-and-push (только на push в main):

Логин в Docker Hub

Сборка образа

Push 1rizhik/devops_hw2:latest

11. CD Pipeline (GitHub Actions)
Файл: .github/workflows/cd.yml

Триггеры:

workflow_run после успешного CI на main

workflow_dispatch (вручную)

Job functional-test:

Checkout

Python 3.12 + requests

Создание .env для docker compose

docker compose up -d --build — полный стек (PostgreSQL + API)

Retry-loop на /health до 30 сек

python scripts/run_scenario.py — 5 сценариев

docker compose exec db psql ... SELECT * FROM predictions — проверка записи в БД

Логи + docker compose down -v

Результаты CD Pipeline:

text
[Health check] status=200
[Predict authentic banknote (request_id=1)] status=200
[Predict fake banknote (request_id=2)] status=200
[Predict not found] status=404
[Predictions history] status=200

All functional tests passed

Verify predictions in database:
 id | request_id | prediction |         created_at
----+------------+------------+----------------------------
  1 |          1 |          0 | 2026-09-14 12:34:28.11615
  2 |          2 |          1 | 2026-09-14 12:34:28.146222
(2 rows)
12. Сценарии тестирования
Файл: config/scenario.json:

Health check — GET /health → 200

Predict authentic — POST /predict {request_id: 1} → prediction=0

Predict fake — POST /predict {request_id: 2} → prediction=1

Predict not found — POST /predict {request_id: 99999} → 404

Predictions history — GET /predictions/1 → 200

13. Ссылки на артефакты
GitHub: https://github.com/1rizhik/devops_hw2

Docker Hub: https://hub.docker.com/r/1rizhik/devops_hw2

Zip-архив: devops_hw2_dist.zip (актуальный)

14. Выводы
Реализовано взаимодействие ML-модели с PostgreSQL по варианту C:

API читает признаки из таблицы requests

Делает предсказание моделью BankNote

Записывает результат в таблицу predictions

Обеспечена безопасность: пароли БД не в коде, только через .env и переменные окружения.

CI Pipeline поднимает PostgreSQL как сервис-контейнер и прогоняет pytest.
CD Pipeline запускает полный стек через docker compose и проводит функциональное тестирование с проверкой записей в БД.

Все требования задания выполнены.