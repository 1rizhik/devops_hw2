"""Flask API: чтение признаков из PostgreSQL, инференс, запись результата."""
import pickle
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, request

from src.db import fetch_predictions, fetch_request_features, save_prediction


MODEL_PATH = Path('models/model.pkl')
FEATURE_NAMES = ['variance', 'skewness', 'curtosis', 'entropy']

app = Flask(__name__)


def load_model():
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200


@app.route('/predict', methods=['POST'])
def predict():
    """Читает features из БД, делает предсказание, сохраняет результат."""
    payload = request.get_json(force=True)
    request_id = payload.get('request_id')
    if request_id is None:
        return jsonify({'error': 'request_id is required'}), 400

    features = fetch_request_features(request_id)
    if features is None:
        return jsonify({'error': f'request_id {request_id} not found'}), 404

    model = load_model()
    X = pd.DataFrame([features], columns=FEATURE_NAMES)
    prediction = int(model.predict(X)[0])

    prediction_id = save_prediction(request_id, prediction)

    return jsonify({
        'request_id': request_id,
        'prediction': prediction,
        'prediction_id': prediction_id,
    }), 200


@app.route('/predictions/<int:request_id>', methods=['GET'])
def get_predictions(request_id: int):
    """Возвращает историю предсказаний для заданного request_id."""
    predictions = fetch_predictions(request_id)
    return jsonify({'request_id': request_id, 'predictions': predictions}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)