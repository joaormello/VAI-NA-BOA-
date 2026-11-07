-- 003_user_profile_and_appointments.sql
-- Fase 10 (Evoluída): Perfil do usuário, Compromissos da Rotina (com suporte a origem fixa ou variável)
-- e Controle Diário de Alertas Escalonados (30, 15, 10, 5, 0 min - SAIA AGORA para Apple Watch)

-- =====================================================================
-- 1. TABELA USER_PROFILE
-- =====================================================================
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL DEFAULT 'João',
    telefone_whatsapp TEXT,
    horario_chegada_padrao TEXT DEFAULT '09:00',
    tolerancia_atraso_min INTEGER DEFAULT 10,
    alertas_padrao TEXT DEFAULT '30,15,10,5,0',
    antecedencia_pergunta_origem_min INTEGER DEFAULT 45,
    dias_monitorados TEXT DEFAULT 'SEG,TER,QUA,QUI,SEX'
);

-- Migra configuração inicial da tabela legada settings (se existir) para user_profile
INSERT INTO user_profile (nome, horario_chegada_padrao, tolerancia_atraso_min, alertas_padrao, dias_monitorados)
SELECT
    'João',
    COALESCE((SELECT horario_chegada FROM settings ORDER BY id DESC LIMIT 1), '09:00'),
    10,
    '30,15,10,5,0',
    'SEG,TER,QUA,QUI,SEX'
WHERE NOT EXISTS (SELECT 1 FROM user_profile);

-- =====================================================================
-- 2. TABELA APPOINTMENTS (COMPROMISSOS / ROTINA DIÁRIA E AVULSOS)
-- =====================================================================
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    origem_id INTEGER NOT NULL,
    origens_alternativas TEXT,
    perguntar_origem INTEGER DEFAULT 0,
    destino_id INTEGER NOT NULL,
    horario_chegada TEXT NOT NULL,
    dias_semana TEXT,
    data_especifica TEXT,
    margem_seguranca_min INTEGER DEFAULT 10,
    alertas_minutos TEXT DEFAULT '30,15,10,5,0',
    ativo INTEGER DEFAULT 1,
    FOREIGN KEY (origem_id) REFERENCES locations(id),
    FOREIGN KEY (destino_id) REFERENCES locations(id)
);

-- =====================================================================
-- 3. TABELA APPOINTMENT_DAILY_STATE (ESTADO DO DIA E ESCALONAMENTO DE ALERTAS)
-- =====================================================================
CREATE TABLE IF NOT EXISTS appointment_daily_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id INTEGER NOT NULL,
    data TEXT NOT NULL,
    origem_escolhida_id INTEGER,
    origem_perguntada INTEGER DEFAULT 0,
    alertas_enviados TEXT DEFAULT '',
    horario_saida_calculado TEXT,
    status TEXT DEFAULT 'PENDENTE',
    UNIQUE(appointment_id, data),
    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE,
    FOREIGN KEY (origem_escolhida_id) REFERENCES locations(id)
);

CREATE INDEX IF NOT EXISTS idx_appointments_ativo
ON appointments (ativo, dias_semana, data_especifica);

CREATE INDEX IF NOT EXISTS idx_daily_state_data
ON appointment_daily_state (data, status);
