-- Script para criar as tabelas no Neon

-- Tabela de Famílias
CREATE TABLE IF NOT EXISTS familias (
    id_familia SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    dependentes INTEGER DEFAULT 0,
    prioridade VARCHAR(50),
    cep VARCHAR(10),
    endereco TEXT,
    lat FLOAT,
    lon FLOAT,
    igreja VARCHAR(255),
    pastor VARCHAR(255),
    ultima_entrega TIMESTAMP,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE
);

-- Tabela de Entregas
CREATE TABLE IF NOT EXISTS entregas (
    id_entrega SERIAL PRIMARY KEY,
    id_familia INTEGER,
    nome_familia VARCHAR(255),
    data TIMESTAMP,
    tipo VARCHAR(255),
    itens TEXT,
    responsavel_entrega VARCHAR(255),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_familia) REFERENCES familias(id_familia)
);

-- Tabela de SOS WhatsApp
CREATE TABLE IF NOT EXISTS sos_whatsapp (
    id_msg SERIAL PRIMARY KEY,
    telefone VARCHAR(20),
    nome VARCHAR(255),
    necessidade VARCHAR(255),
    pessoas INTEGER,
    cep VARCHAR(10),
    endereco TEXT,
    status VARCHAR(50),
    data_hora TIMESTAMP,
    respondido_por VARCHAR(255),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Pessoas Abrigadas
CREATE TABLE IF NOT EXISTS pessoas_abrigadas (
    id_acolhido SERIAL PRIMARY KEY,
    id_local INTEGER,
    nome_responsavel VARCHAR(255),
    qtd_pessoas INTEGER,
    cep_origem VARCHAR(10),
    endereco_origem TEXT,
    lat_origem FLOAT,
    lon_origem FLOAT,
    data_entrada TIMESTAMP,
    responsavel_checkin VARCHAR(255),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Locais de Acolhimento
CREATE TABLE IF NOT EXISTS locais_acolhimento (
    id_local SERIAL PRIMARY KEY,
    nome VARCHAR(255),
    tipo VARCHAR(100),
    capacidade INTEGER,
    cep VARCHAR(10),
    endereco TEXT,
    lat FLOAT,
    lon FLOAT,
    ativo BOOLEAN DEFAULT TRUE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Atendimentos Genéricos
CREATE TABLE IF NOT EXISTS atendimentos (
    id_atendimento SERIAL PRIMARY KEY,
    pessoa_nome VARCHAR(255),
    tipo_atendimento VARCHAR(255),
    descricao TEXT,
    data_atendimento TIMESTAMP,
    status VARCHAR(50),
    responsavel VARCHAR(255),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Catálogo de Itens (Despensa)
CREATE TABLE IF NOT EXISTS catalogo (
    id_item SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    qtd_por_cesta INTEGER DEFAULT 1,
    categoria VARCHAR(100),
    ativo BOOLEAN DEFAULT TRUE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Estoque/Lotes
CREATE TABLE IF NOT EXISTS lotes (
    id_lote SERIAL PRIMARY KEY,
    id_item INTEGER,
    nome_item VARCHAR(255),
    quantidade INTEGER,
    vencimento DATE,
    local_armazenagem VARCHAR(255),
    data_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_item) REFERENCES catalogo(id_item)
);

-- Criar índices para melhorar performance
CREATE INDEX IF NOT EXISTS idx_familias_nome ON familias(nome);
CREATE INDEX IF NOT EXISTS idx_familias_cep ON familias(cep);
CREATE INDEX IF NOT EXISTS idx_sos_status ON sos_whatsapp(status);
CREATE INDEX IF NOT EXISTS idx_acolhido_data ON pessoas_abrigadas(data_entrada);
CREATE INDEX IF NOT EXISTS idx_entrega_data ON entregas(data);
