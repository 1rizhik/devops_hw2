"""Тесты API с реальной БД PostgreSQL для BankNote Authentication."""
import pytest

from src.app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    r = client.get('/health')
    assert r.status_code == 200
    assert r.get_json()['status'] == 'ok'


def test_predict_authentic(client):
    """request_id=1 → признаки подлинной банкноты → класс 0."""
    r = client.post('/predict', json={'request_id': 1})
    assert r.status_code == 200
    data = r.get_json()
    assert data['request_id'] == 1
    assert data['prediction'] == 0
    assert 'prediction_id' in data


def test_predict_fake(client):
    """request_id=2 → признаки поддельной банкноты → класс 1."""
    r = client.post('/predict', json={'request_id': 2})
    assert r.status_code == 200
    assert r.get_json()['prediction'] == 1


def test_predict_missing_request_id(client):
    r = client.post('/predict', json={})
    assert r.status_code == 400


def test_predict_not_found(client):
    r = client.post('/predict', json={'request_id': 99999})
    assert r.status_code == 404


def test_predictions_history(client):
    client.post('/predict', json={'request_id': 1})
    r = client.get('/predictions/1')
    assert r.status_code == 200
    body = r.get_json()
    assert body['request_id'] == 1
    assert len(body['predictions']) >= 1