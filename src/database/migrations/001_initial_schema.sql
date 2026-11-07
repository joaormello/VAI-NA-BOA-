-- 001_initial_schema.sql
-- Garante a existência das tabelas base legadas antes da normalização

CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    apelido TEXT NOT NULL,
    endereco_digitado TEXT,
    endereco_confirmado TEXT,
    latitude REAL,
    longitude REAL
);

CREATE TABLE IF NOT EXISTS traffic_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_hora TEXT,
    origem TEXT,
    destino TEXT,
    distancia_km REAL,
    tempo_minutos INTEGER
);

CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    origem TEXT,
    destino TEXT,
    horario_chegada TEXT
);

CREATE TABLE IF NOT EXISTS favorite_routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    origem TEXT NOT NULL,
    destino TEXT NOT NULL,
    ativo INTEGER DEFAULT 1
);
