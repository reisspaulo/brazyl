-- Brazyl Database Schema
-- PostgreSQL + Supabase
-- Sistema de acompanhamento de políticos brasileiros

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ======================
-- ENUMS
-- ======================

CREATE TYPE plan_type AS ENUM ('FREE', 'BASIC', 'PREMIUM');
CREATE TYPE political_position AS ENUM ('DEPUTADO_FEDERAL', 'SENADOR', 'DEPUTADO_ESTADUAL', 'VEREADOR');
CREATE TYPE event_type AS ENUM ('VOTACAO', 'DESPESA', 'PROJETO_LEI', 'PROPOSTA', 'DISCURSO');
CREATE TYPE notification_status AS ENUM ('PENDING', 'SENT', 'DELIVERED', 'FAILED');

-- ======================
-- TABLES
-- ======================

-- Tabela de Planos
CREATE TABLE plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE,
    type plan_type NOT NULL UNIQUE,
    max_politicians INT NOT NULL,
    notification_frequency VARCHAR(50) NOT NULL, -- 'weekly', 'daily', 'realtime'
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    features JSONB,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de Usuários
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    whatsapp_number VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    cpf VARCHAR(14),
    plan_id UUID REFERENCES plans(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT true,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_interaction_at TIMESTAMP WITH TIME ZONE
);

-- Tabela de Políticos
CREATE TABLE politicians (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(100) UNIQUE, -- ID da API pública (Câmara/Senado)
    name VARCHAR(255) NOT NULL,
    parliamentary_name VARCHAR(255) NOT NULL,
    cpf VARCHAR(14),
    position political_position NOT NULL,
    party VARCHAR(50) NOT NULL,
    state VARCHAR(2) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    photo_url TEXT,
    biography TEXT,
    social_media JSONB, -- {twitter, instagram, facebook, etc}
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes para busca
    CONSTRAINT check_state_uf CHECK (state ~ '^[A-Z]{2}$')
);

-- Tabela de Histórico Político
CREATE TABLE political_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    politician_id UUID REFERENCES politicians(id) ON DELETE CASCADE,
    event_type event_type NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    event_date DATE NOT NULL,
    amount DECIMAL(15, 2), -- Para despesas
    vote_result VARCHAR(50), -- Para votações: 'SIM', 'NAO', 'ABSTENCAO', 'OBSTRUCAO'
    metadata JSONB, -- Dados adicionais específicos do evento
    source_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_politician_events ON political_events(politician_id, event_date DESC)
);

-- Tabela de Seguidores (Relação User <-> Politician)
CREATE TABLE follows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    politician_id UUID REFERENCES politicians(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint para evitar duplicatas
    UNIQUE(user_id, politician_id)
);

-- Tabela de Notificações
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    politician_id UUID REFERENCES politicians(id) ON DELETE SET NULL,
    event_id UUID REFERENCES political_events(id) ON DELETE SET NULL,
    title VARCHAR(500) NOT NULL,
    message TEXT NOT NULL,
    status notification_status DEFAULT 'PENDING',
    scheduled_for TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_user_notifications ON notifications(user_id, created_at DESC),
    INDEX idx_status_scheduled ON notifications(status, scheduled_for)
);

-- ======================
-- INDEXES
-- ======================

CREATE INDEX idx_users_whatsapp ON users(whatsapp_number);
CREATE INDEX idx_users_plan ON users(plan_id);
CREATE INDEX idx_politicians_state ON politicians(state);
CREATE INDEX idx_politicians_party ON politicians(party);
CREATE INDEX idx_politicians_position ON politicians(position);
CREATE INDEX idx_politicians_external ON politicians(external_id);
CREATE INDEX idx_follows_user ON follows(user_id);
CREATE INDEX idx_follows_politician ON follows(politician_id);

-- ======================
-- TRIGGERS (Updated At)
-- ======================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_plans_updated_at BEFORE UPDATE ON plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_politicians_updated_at BEFORE UPDATE ON politicians
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ======================
-- ROW LEVEL SECURITY (RLS)
-- ======================

-- Habilitar RLS nas tabelas
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE politicians ENABLE ROW LEVEL SECURITY;
ALTER TABLE follows ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Políticas básicas (ajustar conforme necessário)
-- Por enquanto, permitir leitura pública em políticos
CREATE POLICY "Políticos são públicos" ON politicians
    FOR SELECT USING (true);

-- Usuários só podem ver seus próprios dados
CREATE POLICY "Usuários veem seus próprios dados" ON users
    FOR SELECT USING (auth.uid() = id);

-- ======================
-- INITIAL DATA
-- ======================

-- Inserir planos padrão
INSERT INTO plans (name, type, max_politicians, notification_frequency, price) VALUES
('Gratuito', 'FREE', 3, 'weekly', 0.00),
('Básico', 'BASIC', 10, 'daily', 9.90),
('Premium', 'PREMIUM', 999, 'realtime', 19.90);

