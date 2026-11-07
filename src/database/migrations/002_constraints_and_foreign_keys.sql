-- 002_constraints_and_foreign_keys.sql
-- 1. Adiciona UNIQUE(apelido) em locations
-- 2. Adiciona UNIQUE(origem, destino) em favorite_routes (removendo duplicatas)
-- 3. Migra traffic_history para usar chaves estrangeiras origem_id e destino_id

-- =====================================================================
-- 1. TABELA LOCATIONS COM UNIQUE(apelido)
-- =====================================================================
CREATE TABLE locations_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    apelido TEXT NOT NULL UNIQUE COLLATE NOCASE,
    endereco_digitado TEXT,
    endereco_confirmado TEXT,
    latitude REAL,
    longitude REAL
);

INSERT OR IGNORE INTO locations_new (id, apelido, endereco_digitado, endereco_confirmado, latitude, longitude)
SELECT id, apelido, endereco_digitado, endereco_confirmado, latitude, longitude
FROM locations;

-- Padroniza variações de endereços antigos no traffic_history para os apelidos já cadastrados
UPDATE traffic_history
SET origem = 'casa'
WHERE origem IN ('Dr. Luiz Migliano, 1870, São Paulo', 'Luiz Migliano, 1870 - São Paulo', 'Dr. Luiz Migliano, 1870');

UPDATE traffic_history
SET destino = 'casa'
WHERE destino IN ('Dr. Luiz Migliano, 1870, São Paulo', 'Luiz Migliano, 1870 - São Paulo', 'Dr. Luiz Migliano, 1870');

UPDATE traffic_history
SET origem = 'C6'
WHERE origem IN (
    'Avenida Nove de Julho, 3186 - Jardim Paulista, São Paulo',
    'Avenida Nove de Julho, São Paulo',
    'Av. Nove de Julho, 3186 - Jardim Paulista, São Paulo - SP, 01406-000'
);

UPDATE traffic_history
SET destino = 'C6'
WHERE destino IN (
    'Avenida Nove de Julho, 3186 - Jardim Paulista, São Paulo',
    'Avenida Nove de Julho, São Paulo',
    'Av. Nove de Julho, 3186 - Jardim Paulista, São Paulo - SP, 01406-000'
);

UPDATE traffic_history
SET origem = 'Enel'
WHERE origem IN ('Enel Morumbi, São Paulo', 'Enem Morumbi, São Paulo');

UPDATE traffic_history
SET destino = 'Enel'
WHERE destino IN ('Enel Morumbi, São Paulo', 'Enem Morumbi, São Paulo');

-- Garante que qualquer outro local histórico existente em traffic_history exista em locations_new
INSERT OR IGNORE INTO locations_new (apelido, endereco_digitado, endereco_confirmado)
SELECT DISTINCT origem, origem, origem
FROM traffic_history
WHERE origem IS NOT NULL;

INSERT OR IGNORE INTO locations_new (apelido, endereco_digitado, endereco_confirmado)
SELECT DISTINCT destino, destino, destino
FROM traffic_history
WHERE destino IS NOT NULL;

DROP TABLE locations;
ALTER TABLE locations_new RENAME TO locations;

-- =====================================================================
-- 2. TABELA FAVORITE_ROUTES COM UNIQUE(origem, destino) E SEM DUPLICATAS
-- =====================================================================
CREATE TABLE favorite_routes_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    origem TEXT NOT NULL,
    destino TEXT NOT NULL,
    ativo INTEGER DEFAULT 1,
    UNIQUE(origem, destino)
);

INSERT OR IGNORE INTO favorite_routes_new (id, origem, destino, ativo)
SELECT MIN(id), origem, destino, MAX(ativo)
FROM favorite_routes
GROUP BY origem, destino;

DROP TABLE favorite_routes;
ALTER TABLE favorite_routes_new RENAME TO favorite_routes;

-- =====================================================================
-- 3. TABELA TRAFFIC_HISTORY COM FOREIGN KEYS (origem_id, destino_id)
-- =====================================================================
CREATE TABLE traffic_history_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_hora TEXT NOT NULL,
    origem_id INTEGER NOT NULL,
    destino_id INTEGER NOT NULL,
    distancia_km REAL,
    tempo_minutos INTEGER,
    FOREIGN KEY (origem_id) REFERENCES locations(id),
    FOREIGN KEY (destino_id) REFERENCES locations(id)
);

INSERT INTO traffic_history_new (id, data_hora, origem_id, destino_id, distancia_km, tempo_minutos)
SELECT
    th.id,
    th.data_hora,
    loc_orig.id,
    loc_dest.id,
    th.distancia_km,
    th.tempo_minutos
FROM traffic_history th
JOIN locations loc_orig ON loc_orig.apelido = th.origem COLLATE NOCASE
JOIN locations loc_dest ON loc_dest.apelido = th.destino COLLATE NOCASE;

DROP TABLE traffic_history;
ALTER TABLE traffic_history_new RENAME TO traffic_history;

CREATE INDEX IF NOT EXISTS idx_traffic_history_rota
ON traffic_history (origem_id, destino_id, data_hora);
