-- Схема для варианта C: чтение признаков + запись результата

CREATE TABLE IF NOT EXISTS requests (
    id SERIAL PRIMARY KEY,
    features JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
    prediction INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_predictions_request_id ON predictions(request_id);

-- Тестовые данные BankNote Authentication
INSERT INTO requests (features) VALUES
    ('[2.3718, 7.4908, 0.015989, -1.7414]'),
    ('[-1.4446, 2.1438, -0.47241, -1.6677]'),
    ('[3.6216, 8.6661, -2.8073, -0.44699]');