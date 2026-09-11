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

-- Тестовые данные (совпадают с scenario.json)
INSERT INTO requests (features) VALUES
    ('[5.1, 3.5, 1.4, 0.2]'),
    ('[6.3, 3.3, 6.0, 2.5]'),
    ('[6.4, 3.2, 4.5, 1.5]');