# 🚀 SCRIPT DE INICIALIZAÇÃO E MIGRAÇÃO DO NEON

import pandas as pd
import datetime
from sqlalchemy import create_engine, text

# ==========================================
# 1. CONFIGURAÇÃO (substitua pela sua URL)
# ==========================================
# Tente ler do secrets, se falhar, usa uma URL padrão (para rodar localmente)
try:
    import streamlit as st
    NEON_URL = st.secrets["postgres"]["url"]
    print("✅ URL do Neon carregada dos secrets.")
except (ImportError, KeyError):
    print("⚠️  Atenção: Rodando fora do Streamlit. Usando URL de exemplo.")
    print("   Edite este script para usar sua URL de conexão real.")
    NEON_URL = "postgresql://neondb_owner:npg_XSbnUR2izB4C@ep-super-hall-adgq7ehk-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# ==========================================
# 2. DEFINIÇÃO DAS TABELAS (Schema SQL)
# ==========================================
SCHEMA_STATEMENTS = [
    """
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
    """,
    """
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
    """,
    """
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
    """,
    """
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
    """,
    """
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
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_local) REFERENCES locais_acolhimento(id_local)
);
    """,
    """
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
    """,
    """
CREATE TABLE IF NOT EXISTS voluntarios (
    id_voluntario SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(255),
    cep VARCHAR(10),
    endereco TEXT,
    possui_veiculo BOOLEAN DEFAULT FALSE,
    tipo_veiculo VARCHAR(100),
    dias_disponiveis TEXT,
    horario_inicio TIME,
    horario_fim TIME,
    observacoes TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE
);
    """,
    """
CREATE TABLE IF NOT EXISTS catalogo (
    id_item SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    qtd_por_cesta INTEGER DEFAULT 1,
    categoria VARCHAR(100),
    ativo BOOLEAN DEFAULT TRUE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
    """,
    """
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
    """,
    "CREATE INDEX IF NOT EXISTS idx_familias_nome ON familias(nome);",
    "CREATE INDEX IF NOT EXISTS idx_familias_cep ON familias(cep);",
    "CREATE INDEX IF NOT EXISTS idx_sos_status ON sos_whatsapp(status);",
    "CREATE INDEX IF NOT EXISTS idx_acolhido_data ON pessoas_abrigadas(data_entrada);",
    "CREATE INDEX IF NOT EXISTS idx_entrega_data ON entregas(data);",
    "CREATE INDEX IF NOT EXISTS idx_catalogo_nome ON catalogo(nome);",
    "CREATE INDEX IF NOT EXISTS idx_lotes_item ON lotes(id_item);"
]

# ==========================================
# 3. DADOS INICIAIS (se necessário)
# ==========================================
DADOS_CATALOGO = [
    # ... (copie os dados do catalogo de 'popular_despensa.py') ...
    {'id_item': 1, 'nome': 'Arroz (5kg)', 'qtd_por_cesta': 1, 'categoria': 'Grãos'},
    # ... etc
]

DADOS_LOTES = [
    # ... (copie os dados dos lotes de 'popular_despensa.py') ...
    {'id_lote': 1, 'id_item': 1, 'quantidade': 25, 'vencimento': datetime.date(2026, 12, 1)},
    # ... etc
]

# ==========================================
# 4. FUNÇÕES DE EXECUÇÃO
# ==========================================
def conectar():
    """Conecta ao Neon e retorna o engine"""
    try:
        engine = create_engine(NEON_URL, pool_pre_ping=True, echo=False)
        with engine.connect() as conn:
            print("✅ Conexão com Neon bem-sucedida!")
        return engine
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return None

def criar_tabelas(engine):
    """Cria todas as tabelas no Neon se não existirem"""
    try:
        with engine.connect() as conn:
            for i, sql in enumerate(SCHEMA_STATEMENTS, 1):
                try:
                    conn.execute(text(sql.strip()))
                    print(f"   ✅ Executado statement {i}/{len(SCHEMA_STATEMENTS)}")
                except Exception as e:
                    print(f"   ⚠️  Erro no statement {i}: {e}")
                    # Continue with next statement
            conn.commit()
            print("✅ Tabelas criadas/verificadas com sucesso!")
            return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def popular_dados_iniciais(engine):
    """Popula as tabelas com dados iniciais (se estiverem vazias)"""
    # Exemplo para catálogo e lotes
    try:
        # Verifica se já tem dados
        df_cat = pd.read_sql("SELECT COUNT(*) FROM catalogo", engine)
        if df_cat['count'][0] == 0:
            print("⏳ Populando tabela 'catalogo' com dados iniciais...")
            df_to_load = pd.DataFrame(DADOS_CATALOGO)
            df_to_load.to_sql('catalogo', engine, if_exists='append', index=False)
            print(f"   -> {len(df_to_load)} itens inseridos.")
        else:
            print("ℹ️  Tabela 'catalogo' já possui dados.")
            
        df_lotes = pd.read_sql("SELECT COUNT(*) FROM lotes", engine)
        if df_lotes['count'][0] == 0:
            print("⏳ Populando tabela 'lotes' com dados iniciais...")
            df_to_load = pd.DataFrame(DADOS_LOTES)
            df_to_load.to_sql('lotes', engine, if_exists='append', index=False)
            print(f"   -> {len(df_to_load)} lotes inseridos.")
        else:
            print("ℹ️  Tabela 'lotes' já possui dados.")
            
        print("✅ Dados iniciais verificados/populados.")
        return True
    except Exception as e:
        print(f"❌ Erro ao popular dados: {e}")
        return False

def verificar_tudo():
    """Executa todo o processo de inicialização"""
    print("🚀 INICIANDO VERIFICAÇÃO DO BANCO DE DADOS NEON 🚀")
    
    engine = conectar()
    if engine:
        if criar_tabelas(engine):
            # Descomente a linha abaixo para popular com dados
            # popular_dados_iniciais(engine)
            print("\n🎉 Tudo pronto! Seu banco de dados está configurado.")
        else:
            print("\n⚠️  Falha na criação das tabelas. O app pode não funcionar.")
    else:
        print("\n⚠️  Não foi possível conectar ao Neon. Verifique a URL.")

# ==========================================
# 5. FUNÇÃO PARA CHAMAR NO APP
# ==========================================
def inicializar_neon():
    """Função para ser chamada no início do app.py"""
    # Esta função pode ser mais leve, apenas criando as tabelas
    engine = conectar()
    if engine:
        criar_tabelas(engine)

if __name__ == "__main__":
    # Executa o script completo ao rodar diretamente
    verificar_tudo()
    print("\nPara usar no seu app, importe e chame `inicializar_neon()`")
