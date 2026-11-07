-- 004_feedback_and_multimodal_routes.sql
-- 1. Adiciona calibração automática (aprendizado com atrasos reais) em appointments
-- 2. Adiciona colunas de feedback pós-chegada em appointment_daily_state
-- 3. Cria tabela route_alternatives para suportar múltiplos modais (Ônibus, Metrô, Carro/Uber) e múltiplas fontes de API

-- =====================================================================
-- 1. CALIBRAÇÃO POR APRENDIZADO EM APPOINTMENTS
-- =====================================================================
ALTER TABLE appointments ADD COLUMN ajuste_aprendizado_min INTEGER DEFAULT 0;

-- =====================================================================
-- 2. FEEDBACK PÓS-CHEGADA EM APPOINTMENT_DAILY_STATE
-- =====================================================================
ALTER TABLE appointment_daily_state ADD COLUMN chegada_confirmada INTEGER DEFAULT 0;
ALTER TABLE appointment_daily_state ADD COLUMN atraso_real_min INTEGER;
ALTER TABLE appointment_daily_state ADD COLUMN modal_utilizado TEXT;
ALTER TABLE appointment_daily_state ADD COLUMN feedback_registrado_em TEXT;
ALTER TABLE appointment_daily_state ADD COLUMN observacao_feedback TEXT;

-- =====================================================================
-- 3. OPÇÕES DE PERCURSO / MODAIS POR ROTA (ÔNIBUS, METRÔ, CARRO)
-- =====================================================================
CREATE TABLE IF NOT EXISTS route_alternatives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    origem_id INTEGER NOT NULL,
    destino_id INTEGER NOT NULL,
    modal TEXT NOT NULL, -- 'ONIBUS', 'METRO', 'METRO_ONIBUS', 'CARRO'
    descricao_percurso TEXT NOT NULL, -- Ex: 'Pegar 2 ônibus (746C-10 + 8605-10)' ou 'Linha 4-Amarela + Linha 1-Azul'
    tempo_base_min INTEGER NOT NULL,
    sensibilidade_transito REAL DEFAULT 1.0, -- 1.0 = sofre 100% com trânsito de rua (ônibus/carro), 0.15 = quase imune (metrô)
    preferencial INTEGER DEFAULT 0,
    ativo INTEGER DEFAULT 1,
    FOREIGN KEY (origem_id) REFERENCES locations(id),
    FOREIGN KEY (destino_id) REFERENCES locations(id)
);

CREATE INDEX IF NOT EXISTS idx_route_alternatives_rota
ON route_alternatives (origem_id, destino_id, ativo);
