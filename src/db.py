"""Подключение к PostgreSQL: чтение requests, запись predictions."""
import json
import os
from contextlib import contextmanager
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_config() -> dict[str, Any]:
    """Читает конфиг БД из переменных окружения (без хардкода секретов)."""
    return {
        'host': os.getenv('POSTGRES_HOST', 'db'),
        'port': int(os.getenv('POSTGRES_PORT', '5432')),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'dbname': os.getenv('POSTGRES_DB'),
    }


@contextmanager
def get_connection():
    """Контекстный менеджер для подключения к БД."""
    conn = psycopg2.connect(**get_db_config())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetch_request_features(request_id: int) -> list[float] | None:
    """Возвращает features для заданного request_id или None."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT features FROM requests WHERE id = %s', (request_id,))
            row = cur.fetchone()
            if not row:
                return None
            features = row['features']
            return features if isinstance(features, list) else json.loads(features)


def save_prediction(request_id: int, prediction: int) -> int:
    """Сохраняет предсказание, возвращает id записи."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO predictions (request_id, prediction) VALUES (%s, %s) RETURNING id',
                (request_id, prediction),
            )
            return cur.fetchone()[0]


def fetch_predictions(request_id: int) -> list[dict]:
    """Возвращает все предсказания по request_id."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                'SELECT id, request_id, prediction, created_at FROM predictions '
                'WHERE request_id = %s ORDER BY id',
                (request_id,),
            )
            return [dict(r) for r in cur.fetchall()]