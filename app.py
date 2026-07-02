import streamlit as st
import pandas as pd
import datetime
import hashlib
import html
import requests
import pydeck as pdk
from streamlit_geolocation import streamlit_geolocation
import time
import folium
from streamlit_folium import st_folium
from sqlalchemy import create_engine
import logging

# Configure logging para debug
logging.basicConfig(level=logging.INFO)

# ==========================================
# CONEXÃO COM NEON
# ==========================================
@st.cache_resource
def get_engine():
    """
    Conecta ao banco Neon usando a URL armazenada nos Secrets.
    """
    try:
        conn_url = st.secrets["postgres"]["url"]
        engine = create_engine(conn_url, pool_pre_ping=True, echo=False)
        return engine
    except Exception as e:
        st.error(f"❌ Erro ao conectar ao Neon: {e}")
        return None


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def carregar_usuario_por_login(login):
    try:
        engine = get_engine()
        if engine is None:
            return None

        query = "SELECT id_usuario, login, nome, senha_hash, perfil, ativo FROM usuarios WHERE login = %(login)s LIMIT 1;"
        df = pd.read_sql_query(query, engine, params={'login': login.lower().strip()})
        if df.empty:
            return None
        return df.iloc[0].to_dict()
    except Exception as e:
        logging.warning(f"Não foi possível carregar usuário do Neon: {e}")
        return None


def validar_usuario(login, senha):
    login_canonico = login.lower().strip()
    usuario = carregar_usuario_por_login(login_canonico)
    if usuario and usuario.get('ativo', True):
        if usuario['senha_hash'] == hash_password(senha):
            usuario['login'] = usuario['login'].lower().strip()
            usuario['nome'] = usuario.get('nome') or usuario['login']
            return usuario

    if login_canonico == 'admin' and senha == 'pibjf':
        return {'login': 'admin', 'nome': 'Administrador', 'perfil': 'admin', 'ativo': True}
    if login_canonico == 'master' and senha == 'pibjf':
        return {'login': 'master', 'nome': 'Master', 'perfil': 'master', 'ativo': True}
    return None


def carregar_usuarios_neon():
    try:
        engine = get_engine()
        if engine is None:
            return None

        query = "SELECT id_usuario, login, nome, perfil, ativo FROM usuarios ORDER BY id_usuario;"
        df = pd.read_sql_query(query, engine)
        if 'ativo' in df.columns:
            df['ativo'] = df['ativo'].fillna(True)
        return df
    except Exception as e:
        logging.warning(f"Não foi possível carregar usuários do Neon: {e}")
        return None


def salvar_usuario_neon(dados_usuario):
    try:
        engine = get_engine()
        if engine is None:
            return False

        dados_usuario = dados_usuario.copy()
        dados_usuario.pop('id_usuario', None)
        senha = dados_usuario.pop('senha', None)
        dados_usuario['senha_hash'] = hash_password(senha or '')
        dados_usuario['login'] = dados_usuario.get('login', '').lower().strip()
        df = pd.DataFrame([dados_usuario])
        df.to_sql('usuarios', engine, if_exists='append', index=False)
        st.success("✅ Usuário salvo no Neon com sucesso!")
        return True
    except Exception as e:
        st.warning(f"⚠️ Erro ao salvar usuário no Neon: {e}")
        return False


def set_usuario_ativo_neon(id_usuario, ativo=True):
    try:
        engine = get_engine()
        if engine is None:
            return False

        from sqlalchemy import text
        with engine.begin() as conn:
            conn.execute(text("UPDATE usuarios SET ativo = :ativo WHERE id_usuario = :id"), {'ativo': ativo, 'id': id_usuario})
        return True
    except Exception as e:
        logging.warning(f"Não foi possível atualizar status do usuário no Neon: {e}")
        return False


def salvar_familia_neon(dados_familia):
    """Salva dados de uma família no Neon"""
    try:
        engine = get_engine()
        if engine is None:
            return False

        dados_familia = dados_familia.copy()
        dados_familia.pop('id_familia', None)
        if 'data_cadastro' not in dados_familia or not dados_familia['data_cadastro']:
            dados_familia['data_cadastro'] = datetime.datetime.now()
        df = pd.DataFrame([dados_familia])
        df.to_sql('familias', engine, if_exists='append', index=False)
        st.success("✅ Família salva no Neon com sucesso!")
        return True
    except Exception as e:
        st.warning(f"⚠️ Erro ao salvar família no Neon: {e}")
        return False


def excluir_familia_neon(id_familia):
    """Marca família como inativa no Neon."""
    try:
        engine = get_engine()
        if engine is None:
            return False

        from sqlalchemy import text
        with engine.begin() as conn:
            conn.execute(text("UPDATE familias SET ativo = FALSE WHERE id_familia = :id"), {'id': id_familia})
        return True
    except Exception as e:
        logging.warning(f"Não foi possível excluir família no Neon: {e}")
        return False


def salvar_entrega_neon(dados_entrega):
    """Salva dados de uma entrega no Neon"""
    try:
        engine = get_engine()
        if engine is None:
            return False

        dados_entrega = dados_entrega.copy()
        dados_entrega.pop('id_entrega', None)
        df = pd.DataFrame([dados_entrega])
        df.to_sql('entregas', engine, if_exists='append', index=False)
        st.success("✅ Entrega registrada no Neon com sucesso!")
        return True
    except Exception as e:
        st.warning(f"⚠️ Erro ao salvar entrega no Neon: {e}")
        return False

def salvar_sos_neon(dados_sos):
    """Salva dados de SOS/WhatsApp no Neon"""
    try:
        engine = get_engine()
        if engine is None:
            return False
        
        df = pd.DataFrame([dados_sos])
        df.to_sql('sos_whatsapp', engine, if_exists='append', index=False)
        st.success("✅ SOS registrado no Neon com sucesso!")
        return True
    except Exception as e:
        st.warning(f"⚠️ Erro ao salvar SOS no Neon: {e}")
        return False

def salvar_acolhimento_neon(dados_acolhimento):
    """Salva dados de acolhimento no Neon"""
    try:
        engine = get_engine()
        if engine is None:
            return False
        
        df = pd.DataFrame([dados_acolhimento])
        df.to_sql('pessoas_abrigadas', engine, if_exists='append', index=False)
        st.success("✅ Acolhimento registrado no Neon com sucesso!")
        return True
    except Exception as e:
        st.warning(f"⚠️ Erro ao salvar acolhimento no Neon: {e}")
        return False

def salvar_atendimento_neon(dados):
    """Salva dados de atendimento no Neon (genérico)"""
    try:
        engine = get_engine()
        if engine is None:
            return False
        
        df = pd.DataFrame([dados])
        df.to_sql('atendimentos', engine, if_exists='append', index=False)
        st.success("✅ Dados enviados ao Neon com sucesso!")
        return True
    except Exception as e:
        st.warning(f"⚠️ Erro ao salvar atendimento no Neon: {e}")
        return False

def salvar_voluntario_neon(dados_voluntario):
    """Salva dados de um voluntário no Neon"""
    try:
        engine = get_engine()
        if engine is None:
            return False
        df = pd.DataFrame([dados_voluntario])
        df.to_sql('voluntarios', engine, if_exists='append', index=False)
        st.success("✅ Voluntário salvo no Neon com sucesso!")
        return True
    except Exception as e:
        st.warning(f"⚠️ Erro ao salvar voluntário no Neon: {e}")
        return False

def salvar_item_catalogo_neon(dados_item):
    """Salva um novo item no catálogo de despensa do Neon"""
    try:
        engine = get_engine()
        if engine is None:
            return False

        dados_item = dados_item.copy()
        if 'categoria' not in dados_item:
            dados_item['categoria'] = 'Avulso'
        if 'qtd_por_cesta' not in dados_item:
            dados_item['qtd_por_cesta'] = 0

        dados_item.pop('id_item', None)
        df = pd.DataFrame([dados_item])
        df.to_sql('catalogo', engine, if_exists='append', index=False)
        st.success("✅ Item adicionado ao catálogo de despensa!")
        return True
    except Exception as e:
        st.warning(f"⚠️ Erro ao salvar item: {e}")
        return False

def salvar_lote_neon(dados_lote):
    """Salva um novo lote de estoque no Neon"""
    try:
        engine = get_engine()
        if engine is None:
            return False

        dados_lote = dados_lote.copy()
        if 'nome_item' not in dados_lote:
            dados_lote['nome_item'] = ''

        dados_lote.pop('id_lote', None)
        df = pd.DataFrame([dados_lote])
        df.to_sql('lotes', engine, if_exists='append', index=False)
        st.success("✅ Lote de estoque registrado com sucesso!")
        return True
    except Exception as e:
        st.warning(f"⚠️ Erro ao salvar lote: {e}")
        return False


def salvar_parceiro_neon(dados_parceiro):
    """Salva dados de parceiros no Neon"""
    try:
        engine = get_engine()
        if engine is None:
            return False

        dados_parceiro = dados_parceiro.copy()
        dados_parceiro.pop('id_parceiro', None)
        if 'data_cadastro' not in dados_parceiro or not dados_parceiro['data_cadastro']:
            dados_parceiro['data_cadastro'] = datetime.datetime.now()
        df = pd.DataFrame([dados_parceiro])
        df.to_sql('parceiros', engine, if_exists='append', index=False)
        st.success("✅ Parceiro salvo no Neon com sucesso!")
        return True
    except Exception as e:
        st.warning(f"⚠️ Erro ao salvar parceiro no Neon: {e}")
        return False


def carregar_catalogo_neon():
    """Carrega o catálogo de itens a partir do Neon."""
    try:
        engine = get_engine()
        if engine is None:
            return None

        query = "SELECT id_item, nome, qtd_por_cesta, categoria FROM catalogo WHERE ativo = TRUE ORDER BY id_item;"
        df = pd.read_sql_query(query, engine)
        if 'categoria' not in df.columns:
            df['categoria'] = 'Extra'
        df['qtd_por_cesta'] = df['qtd_por_cesta'].fillna(0).astype(int)
        return df
    except Exception as e:
        logging.warning(f"Não foi possível carregar catálogo do Neon: {e}")
        return None


def carregar_lotes_neon():
    """Carrega os lotes de estoque a partir do Neon."""
    try:
        engine = get_engine()
        if engine is None:
            return None

        query = "SELECT id_lote, id_item, nome_item, quantidade, vencimento, local_armazenagem, data_entrada, ativo FROM lotes WHERE ativo = TRUE ORDER BY vencimento;"
        df = pd.read_sql_query(query, engine)
        if 'nome_item' not in df.columns:
            df['nome_item'] = None
        if 'quantidade' in df.columns:
            df['quantidade'] = df['quantidade'].fillna(0).astype(int)
        return df
    except Exception as e:
        logging.warning(f"Não foi possível carregar lotes do Neon: {e}")
        return None


def carregar_familias_neon():
    """Carrega as famílias ativas a partir do Neon."""
    try:
        engine = get_engine()
        if engine is None:
            return None

        query = "SELECT id_familia, nome, dependentes, prioridade, telefone, atendimento_tipo, cep, endereco, lat, lon, igreja, pastor, ultima_entrega, data_cadastro FROM familias WHERE ativo = TRUE ORDER BY id_familia;"
        df = pd.read_sql_query(query, engine)

        if 'dependentes' in df.columns:
            df['dependentes'] = df['dependentes'].fillna(0).astype(int)
        if 'telefone' in df.columns:
            df['telefone'] = df['telefone'].fillna('')
        if 'atendimento_tipo' in df.columns:
            df['atendimento_tipo'] = df['atendimento_tipo'].fillna('Esporádico')
        if 'data_cadastro' in df.columns:
            df['data_cadastro'] = pd.to_datetime(df['data_cadastro'], errors='coerce')
        return df
    except Exception as e:
        logging.warning(f"Não foi possível carregar famílias do Neon: {e}")
        return None


def carregar_entregas_neon():
    """Carrega o histórico de entregas a partir do Neon."""
    try:
        engine = get_engine()
        if engine is None:
            return None

        query = "SELECT id_entrega, nome_familia, data, tipo FROM entregas ORDER BY id_entrega DESC;"
        df = pd.read_sql_query(query, engine)
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data']).dt.date
        return df
    except Exception as e:
        logging.warning(f"Não foi possível carregar entregas do Neon: {e}")
        return None


def carregar_voluntarios_neon():
    """Carrega os voluntários ativos a partir do Neon."""
    try:
        engine = get_engine()
        if engine is None:
            return None

        query = """
            SELECT id_voluntario, nome, telefone, email, cep, endereco,
                   possui_veiculo, tipo_veiculo, dias_disponiveis,
                   horario_inicio, horario_fim, observacoes, data_cadastro, ativo
            FROM voluntarios
            WHERE ativo = TRUE
            ORDER BY id_voluntario;
        """
        df = pd.read_sql_query(query, engine)
        if df.empty:
            return df
        if 'possui_veiculo' in df.columns:
            df['possui_veiculo'] = df['possui_veiculo'].fillna(False).astype(bool)
        if 'ativo' in df.columns:
            df['ativo'] = df['ativo'].fillna(True)
        if 'data_cadastro' in df.columns:
            df['data_cadastro'] = pd.to_datetime(df['data_cadastro'], errors='coerce')
        return df
    except Exception as e:
        logging.warning(f"Não foi possível carregar voluntários do Neon: {e}")
        return None


def refresh_estoque_neon(force=False):
    """Atualiza o estoque local a partir dos dados do Neon."""
    now = datetime.datetime.now()
    if not force and 'last_estoque_refresh' in st.session_state:
        delta = now - st.session_state.last_estoque_refresh
        if delta.total_seconds() < 15:
            return

    cat = carregar_catalogo_neon()
    lot = carregar_lotes_neon()
    fam = carregar_familias_neon()
    ent = carregar_entregas_neon()
    vol = carregar_voluntarios_neon()
    if cat is not None:
        st.session_state.db_catalogo = cat
    if lot is not None:
        st.session_state.db_lotes = lot
    if fam is not None:
        st.session_state.db_familias = fam
    if ent is not None:
        st.session_state.db_entregas = ent
    if vol is not None:
        st.session_state.db_voluntarios = vol
    st.session_state.last_estoque_refresh = now

# ==========================================
# FUNÇÃO DE INICIALIZAÇÃO DO NEON
# ==========================================
@st.cache_resource
def inicializar_neon():
    """Conecta e cria todas as tabelas no Neon se não existirem."""
    try:
        engine = get_engine()
        if engine is None:
            st.error("Falha na conexão inicial com Neon. Verifique as configurações.")
            return

        # Lista de statements SQL separados para evitar timeout SSL
        schema_statements = [
            "CREATE TABLE IF NOT EXISTS familias (id_familia SERIAL PRIMARY KEY, nome VARCHAR(255) NOT NULL, dependentes INTEGER, prioridade VARCHAR(50), telefone VARCHAR(30), atendimento_tipo VARCHAR(50), cep VARCHAR(10), endereco TEXT, lat FLOAT, lon FLOAT, igreja VARCHAR(255), pastor VARCHAR(255), ultima_entrega TIMESTAMP, data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP, ativo BOOLEAN DEFAULT TRUE);",
            "ALTER TABLE familias ADD COLUMN IF NOT EXISTS telefone VARCHAR(30);",
            "ALTER TABLE familias ADD COLUMN IF NOT EXISTS atendimento_tipo VARCHAR(50);",
            "CREATE TABLE IF NOT EXISTS entregas (id_entrega SERIAL PRIMARY KEY, id_familia INTEGER, nome_familia VARCHAR(255), data TIMESTAMP, tipo VARCHAR(255), itens TEXT, responsavel_entrega VARCHAR(255), data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (id_familia) REFERENCES familias(id_familia));",
            "CREATE TABLE IF NOT EXISTS sos_whatsapp (id_msg SERIAL PRIMARY KEY, telefone VARCHAR(20), nome VARCHAR(255), necessidade VARCHAR(255), pessoas INTEGER, cep VARCHAR(10), endereco TEXT, status VARCHAR(50), data_hora TIMESTAMP, respondido_por VARCHAR(255), data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
            "CREATE TABLE IF NOT EXISTS locais_acolhimento (id_local SERIAL PRIMARY KEY, nome VARCHAR(255), tipo VARCHAR(100), capacidade INTEGER, cep VARCHAR(10), endereco TEXT, lat FLOAT, lon FLOAT, ativo BOOLEAN DEFAULT TRUE, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
            "CREATE TABLE IF NOT EXISTS pessoas_abrigadas (id_acolhido SERIAL PRIMARY KEY, id_local INTEGER, nome_responsavel VARCHAR(255), qtd_pessoas INTEGER, cep_origem VARCHAR(10), endereco_origem TEXT, lat_origem FLOAT, lon_origem FLOAT, data_entrada TIMESTAMP, responsavel_checkin VARCHAR(255), data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (id_local) REFERENCES locais_acolhimento(id_local));",
            "CREATE TABLE IF NOT EXISTS atendimentos (id_atendimento SERIAL PRIMARY KEY, pessoa_nome VARCHAR(255), tipo_atendimento VARCHAR(255), descricao TEXT, data_atendimento TIMESTAMP, status VARCHAR(50), responsavel VARCHAR(255), data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
            "CREATE TABLE IF NOT EXISTS voluntarios (id_voluntario SERIAL PRIMARY KEY, nome VARCHAR(255) NOT NULL, telefone VARCHAR(20), email VARCHAR(255), cep VARCHAR(10), endereco TEXT, possui_veiculo BOOLEAN DEFAULT FALSE, tipo_veiculo VARCHAR(100), dias_disponiveis TEXT, horario_inicio TIME, horario_fim TIME, observacoes TEXT, data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP, ativo BOOLEAN DEFAULT TRUE);",
            "CREATE TABLE IF NOT EXISTS usuarios (id_usuario SERIAL PRIMARY KEY, login VARCHAR(100) UNIQUE NOT NULL, nome VARCHAR(255), senha_hash VARCHAR(255) NOT NULL, perfil VARCHAR(50) NOT NULL, ativo BOOLEAN DEFAULT TRUE, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS abas_acesso TEXT;",
            "CREATE TABLE IF NOT EXISTS catalogo (id_item SERIAL PRIMARY KEY, nome VARCHAR(255) NOT NULL, qtd_por_cesta INTEGER DEFAULT 1, categoria VARCHAR(100), ativo BOOLEAN DEFAULT TRUE, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
            "CREATE TABLE IF NOT EXISTS lotes (id_lote SERIAL PRIMARY KEY, id_item INTEGER, nome_item VARCHAR(255), quantidade INTEGER, vencimento DATE, local_armazenagem VARCHAR(255), data_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP, ativo BOOLEAN DEFAULT TRUE, FOREIGN KEY (id_item) REFERENCES catalogo(id_item));",
            "CREATE TABLE IF NOT EXISTS parceiros (id_parceiro SERIAL PRIMARY KEY, tipo_pessoa VARCHAR(50), nome VARCHAR(255) NOT NULL, documento VARCHAR(50), telefone VARCHAR(20), email VARCHAR(255), cep VARCHAR(10), endereco TEXT, contato_preferencial VARCHAR(20), alerta_mensal BOOLEAN DEFAULT FALSE, alerta_anual BOOLEAN DEFAULT FALSE, ultimo_agradecimento_mensal TIMESTAMP, ultimo_agradecimento_anual TIMESTAMP, itens_ajuda TEXT, data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP, ativo BOOLEAN DEFAULT TRUE);",
            "CREATE INDEX IF NOT EXISTS idx_familias_nome ON familias(nome);",
            "CREATE INDEX IF NOT EXISTS idx_parceiros_nome ON parceiros(nome);",
            "CREATE INDEX IF NOT EXISTS idx_sos_status ON sos_whatsapp(status);",
            "CREATE INDEX IF NOT EXISTS idx_usuarios_login ON usuarios(login);"
        ]

        with engine.connect() as conn:
            from sqlalchemy import text
            for sql in schema_statements:
                try:
                    conn.execute(text(sql))
                except Exception as stmt_error:
                    logging.warning(f"Statement falhou (pode ser normal se tabela já existe): {stmt_error}")
            conn.commit()

            try:
                usuarios_count = conn.execute(text("SELECT COUNT(*) FROM usuarios;")).scalar()
                if usuarios_count == 0:
                    senha_padrao = hash_password('pibjf')
                    conn.execute(text(
                        "INSERT INTO usuarios (login, nome, senha_hash, perfil, ativo) VALUES "
                        "(:login_admin, :nome_admin, :senha, :perfil_admin, TRUE), "
                        "(:login_master, :nome_master, :senha, :perfil_master, TRUE);"
                    ), {
                        'login_admin': 'admin',
                        'nome_admin': 'Administrador',
                        'login_master': 'master',
                        'nome_master': 'Master',
                        'senha': senha_padrao,
                        'perfil_admin': 'admin',
                        'perfil_master': 'master'
                    })
                    logging.info("Usuários padrão criados no Neon: admin e master.")
            except Exception as default_user_error:
                logging.warning(f"Não foi possível criar usuário padrão no Neon: {default_user_error}")
            
        logging.info("🚀 Banco de dados Neon inicializado com sucesso!")
        
    except Exception as e:
        st.error(f"❌ Erro crítico ao inicializar o banco de dados: {e}")
        logging.error(f"Erro na inicialização do Neon: {e}")

# Chame a função de inicialização uma vez ao iniciar o app
inicializar_neon()

# ==========================================
# 1. RENDERIZAÇÃO DE MAPAS
# ==========================================

def renderizar_mapa_folium(df_mapa):
    """
    Renderiza um mapa 2D leve e infalível usando Folium.
    """
    # Limpa dados sem GPS
    df_mapa = df_mapa.dropna(subset=['lat', 'lon']).copy()
    
    if df_mapa.empty:
        st.warning("⚠️ Não há dados de GPS para exibir no mapa.")
        return

    # Centro do mapa (Média dos pontos)
    lat_media = df_mapa['lat'].mean()
    lon_media = df_mapa['lon'].mean()

    # Cria o mapa base (OpenStreetMap)
    m = folium.Map(location=[lat_media, lon_media], zoom_start=13, control_scale=True)

    # Adiciona os marcadores
    for _, row in df_mapa.iterrows():
        # Define cor baseada no tipo ou contexto
        # Se vier do 'color' hexadecimal antigo, convertemos para nomes do Folium
        cor_icone = 'gray' # Padrão
        
        # Lógica de cores simples
        tipo = str(row.get('tipo', '')).lower()
        if 'voluntario' in tipo or 'você' in tipo:
            cor_icone = 'blue'
            icone_fa = 'user'
        elif 'familia' in tipo or 'risco' in tipo:
            cor_icone = 'red'
            icone_fa = 'home'
        elif 'abrigo' in tipo or 'seguro' in tipo:
            cor_icone = 'green'
            icone_fa = 'shield'
        
        # Cria o Popup com HTML bonito
        html_popup = f"""
        <div style='font-family: sans-serif; width: 200px;'>
            <h4 style='margin-bottom:5px; color: #333;'>{row.get('nome', 'Sem nome')}</h4>
            <p style='font-size:12px; margin:0;'>{row.get('endereco', '')}</p>
        </div>
        """
        
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=folium.Popup(html_popup, max_width=250),
            tooltip=row.get('nome', 'Ver detalhes'),
            icon=folium.Icon(color=cor_icone, icon=icone_fa, prefix='fa')
        ).add_to(m)

    # Exibe no Streamlit (usa toda a largura disponível)
    st_folium(m, width=None, height=500, use_container_width=True)
    
# ==========================================
# 1. CONFIGURAÇÃO E DESIGN SYSTEM
# ==========================================
st.set_page_config(
    page_title="Atos 4. 34", 
    layout="wide", 
    page_icon="🕊️",
    initial_sidebar_state="expanded"
)

# --- CSS MODERNO E ACESSÍVEL PARA PESSOAS SIMPLES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    :root {
        --primary: #60a5fa;
        --primary-light: #93c5fd;
        --primary-dark: #2563eb;
        --success: #34d399;
        --warning: #fbbf24;
        --danger: #f87171;
        --bg-app: #0f172a;
        --bg-card: #111827;
        --text-main: #e2e8f0;
        --text-light: #94a3b8;
        --border: #334155;
        --shadow: 0 20px 50px rgba(0,0,0,0.35);
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif;
        background-color: var(--bg-app);
        color: var(--text-main);
        font-size: 16px;
        line-height: 1.6;
    }
    
    .stApp { background-color: var(--bg-app); }

    /* CSS COMPATÍVEL COM CLASSES ANTIGAS E NOVAS */
    .bento-card, .card {
        background: var(--bg-card);
        padding: 24px;
        border-radius: 12px;
        border: 1px solid var(--border);
        box-shadow: var(--shadow);
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }
    .bento-card:hover, .card:hover {
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }

    /* TÍTULOS - Grandes e Claros */
    .title-modern, h1, h2, h3 { 
        color: var(--text-main);
        font-weight: 700;
        margin: 20px 0 12px 0;
        line-height: 1.3;
    }
    .title-modern { font-size: 24px; margin-top: 0; }
    .subtitle-modern { color: var(--text-light); font-weight: 500; font-size: 14px; margin-bottom: 12px; }
    
    h1 { font-size: 32px; }
    h2 { font-size: 24px; }
    h3 { font-size: 18px; }

    /* BADGES/TAGS - Coloridos e Grandes */
    .badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 13px;
        margin: 4px;
    }
    .badge-success { background: #164e3b; color: #a7f3d0; }
    .badge-warning { background: #92400e; color: #fef3c7; }
    .badge-danger { background: #7f1d1d; color: #fee2e2; }
    .badge-info { background: #1e3a8a; color: #dbeafe; }

    /* BOTÕES - Maiores e Mais Visíveis */
    .stButton > button {
        font-size: 16px !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        border: none !important;
        transition: transform 0.28s ease, box-shadow 0.28s ease, background-color 0.28s ease !important;
        height: auto !important;
        min-height: 48px !important;
        background: linear-gradient(135deg, #60a5fa 0%, #2563eb 100%) !important;
        color: white !important;
        box-shadow: 0 12px 30px rgba(96,165,250,0.18) !important;
    }
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 18px 50px rgba(96,165,250,0.28) !important;
        background: linear-gradient(135deg, #93c5fd 0%, #3b82f6 100%) !important;
    }
    .stButton > button:active {
        transform: translateY(-1px) scale(0.995);
    }

    /* TEXTOS DE ENTRADA - Maiores */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        font-size: 15px !important;
        padding: 14px 16px !important;
        border-radius: 14px !important;
        min-height: 48px !important;
        background: #0f172a !important;
        border: 1px solid #334155 !important;
        color: #e2e8f0 !important;
        box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.65) !important;
        transition: border-color 0.28s ease, box-shadow 0.28s ease, background 0.28s ease !important;
    }
    .stTextInput > div > div > input:hover,
    .stNumberInput > div > div > input:hover,
    .stSelectbox > div > div > select:hover,
    .stTextArea > div > div > textarea:hover {
        border-color: #475569 !important;
    }
    .stTextInput > div > div > input::placeholder,
    .stNumberInput > div > div > input::placeholder,
    .stSelectbox > div > div > select::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #94a3b8 !important;
        opacity: 1 !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {
        outline: none !important;
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 4px rgba(96,165,250,0.16) !important;
        background: #111827 !important;
    }

    /* MENU/TABS NA SIDEBAR COM CORES */
    .menu-item {
        display: block;
        padding: 12px 16px;
        margin: 8px 0;
        background: var(--bg-card);
        border-radius: 8px;
        border-left: 4px solid transparent;
        cursor: pointer;
        font-weight: 500;
        font-size: 15px;
        transition: all 0.2s;
        border: 1px solid var(--border);
    }
    .menu-item:hover {
        background: #1e293b;
        border-left-color: var(--primary);
    }
    .menu-item.active {
        background: var(--primary);
        color: white;
        border: 1px solid var(--primary);
    }

    /* LOGIN - Mais Acessível */
    .login-box {
        background: rgba(15, 23, 42, 0.92);
        border: 1px solid rgba(148, 163, 184, 0.16);
        backdrop-filter: blur(20px);
        padding: 44px 36px;
        border-radius: 30px;
        box-shadow: 0 30px 80px rgba(0, 0, 0, 0.45);
        max-width: 460px;
        margin: auto;
        position: relative;
        overflow: hidden;
    }
    .login-box::before {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.14), transparent 40%, rgba(59, 130, 246, 0.06));
        pointer-events: none;
    }
    .login-box > * {
        position: relative;
        z-index: 1;
    }
    .login-box h1 {
        font-size: 36px;
        margin-bottom: 10px;
        color: #93c5fd;
        letter-spacing: -0.03em;
    }
    .login-box p {
        color: #cbd5e1;
        margin-bottom: 30px;
        font-size: 15px;
        line-height: 1.7;
    }
    .login-box .login-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 14px;
        border-radius: 999px;
        background: rgba(96, 165, 250, 0.18);
        color: #bfdbfe;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 18px;
    }
    .login-box .login-hero {
        color: #e2e8f0;
        font-size: 14px;
        margin-bottom: 32px;
    }

    /* TABELAS - Legíveis */
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th {
        background: #1e293b;
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: 600;
    }
    td {
        padding: 12px;
        border-bottom: 1px solid var(--border);
    }
    tr:hover { background: #111827; }

    /* FORMULÁRIOS - Bem Espaçados */
    form {
        max-width: 600px;
    }
    label {
        font-weight: 600;
        margin-bottom: 6px;
        display: block;
        font-size: 15px;
    }

    /* SIDEBAR - Limpo */
    [data-testid="stSidebar"] {
        background-color: var(--bg-card);
        border-right: 1px solid var(--border);
        padding: 20px 16px;
        color: var(--text-main);
    }
    [data-testid="stSidebar"] * {
        color: var(--text-main) !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background-color: var(--primary) !important;
        color: white !important;
    }

    /* ALERTAS - Grandes e Claros */
    .stAlert { 
        padding: 16px !important;
        border-radius: 8px !important;
        font-size: 15px !important;
        margin: 12px 0 !important;
    }

    /* MÉTRICA/KPI - Destaca Informações */
    .metric-box {
        background: var(--primary);
        color: white;
        padding: 24px;
        border-radius: 8px;
        text-align: center;
        margin: 12px 0;
    }
    .metric-box .number {
        font-size: 36px;
        font-weight: 700;
    }
    .metric-box .label {
        font-size: 14px;
        opacity: 0.9;
        margin-top: 8px;
    }

    /* RESPONSIVIDADE */
    @media (max-width: 768px) {
        h1 { font-size: 24px; }
        h2 { font-size: 20px; }
        .stButton > button { min-height: 50px !important; }
    }
    
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SISTEMA DE LOGIN E AUTENTICAÇÃO
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'user_login' not in st.session_state:
    st.session_state.user_login = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'force_password_change' not in st.session_state:
    st.session_state.force_password_change = False

def login_page():
    # Centraliza o conteúdo vertical e horizontalmente usando colunas
    st.markdown("", unsafe_allow_html=True) 
    col1, col2, col3 = st.columns([1, 1, 1]) # Ajuste para telas grandes
    
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="login-box">
            <span class="login-badge">🔒 Acesso Seguro</span>
            <h1>Atos 4</h1>
            <p class="login-hero">Bem-vindo ao painel da comunidade. Entre com seu usuário para continuar.</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            usuario = st.text_input("Usuário", placeholder="admin")
            senha = st.text_input("Senha", type="password", placeholder="••••••")
            submit = st.form_submit_button("Entrar no Sistema", use_container_width=True, type="primary")

            if submit:
                if usuario and senha:
                    usuario_info = validar_usuario(usuario, senha)
                    if usuario_info:
                        st.session_state.authenticated = True
                        st.session_state.current_user = usuario_info.get('nome', usuario_info['login'])
                        st.session_state.user_login = usuario_info['login']
                        st.session_state.user_role = usuario_info['perfil']
                        st.session_state.force_password_change = is_default_password(usuario_info['login'], senha)
                        if st.session_state.force_password_change:
                            st.warning("Você está usando a senha inicial. Por favor, altere sua senha antes de continuar.")
                        else:
                            st.toast("Login realizado com sucesso!", icon="🎉")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Credenciais inválidas. Tente novamente.")
                else:
                    st.error("Preencha usuário e senha.")

        st.markdown("""
            <div style='text-align: center; margin-top: 20px; color: #94A3B8; font-size: 12px;'>
                Esqueceu a senha? Contate o administrador da igreja.
            </div>
        """, unsafe_allow_html=True)

def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.user_login = None
    st.session_state.user_role = None
    st.session_state.force_password_change = False
    st.rerun()


# ==========================================
# GERENCIAMENTO DE PERMISSÕES E SENHAS
# ==========================================
def alterar_senha_neon(login, senha_nova):
    """Altera a senha de um usuário no Neon"""
    try:
        engine = get_engine()
        if engine is None:
            return False
        
        from sqlalchemy import text
        login_clean = login.lower().strip()
        nova_hash = hash_password(senha_nova)
        with engine.begin() as conn:
            result = conn.execute(
                text("UPDATE usuarios SET senha_hash = :senha WHERE lower(login) = :login"),
                {'senha': nova_hash, 'login': login_clean}
            )
            if result.rowcount == 0 and login_clean in ('admin', 'master'):
                nome_default = 'Administrador' if login_clean == 'admin' else 'Master'
                conn.execute(
                    text(
                        "INSERT INTO usuarios (login, nome, senha_hash, perfil, ativo) "
                        "VALUES (:login, :nome, :senha, :perfil, TRUE)"
                    ),
                    {
                        'login': login_clean,
                        'nome': nome_default,
                        'senha': nova_hash,
                        'perfil': login_clean
                    }
                )
        return True
    except Exception as e:
        logging.warning(f"Erro ao alterar senha: {e}")
        return False


def is_default_password(login, senha):
    """Verifica se o login está usando a senha padrão para forçar alteração."""
    if login in ('admin', 'master') and senha == 'pibjf':
        return True
    usuario = carregar_usuario_por_login(login)
    if usuario is None:
        return False
    return usuario.get('senha_hash') == hash_password('pibjf')


def carregar_permissoes_abas_neon(login):
    """Carrega as abas permitidas para um usuário"""
    try:
        engine = get_engine()
        if engine is None:
            return None
        
        query = "SELECT abas_acesso FROM usuarios WHERE login = %(login)s LIMIT 1;"
        df = pd.read_sql_query(query, engine, params={'login': login})
        if df.empty:
            return None
        
        abas_str = df.iloc[0]['abas_acesso']
        if abas_str is None:
            return None
        if isinstance(abas_str, str):
            abas = [aba.strip() for aba in abas_str.split(',') if aba.strip()]
            return abas if abas else None
        return None
    except Exception as e:
        logging.warning(f"Erro ao carregar permissões de abas: {e}")
        return None


def obter_abas_permitidas(login, perfil):
    """Retorna as abas que o usuário pode acessar, usando permissões customizadas ou o padrão do perfil."""
    permissoes_abas = carregar_permissoes_abas_neon(login)
    if permissoes_abas:
        return permissoes_abas
    abas_padrao = obter_abas_padrao_por_perfil(perfil)
    return abas_padrao or ["Dashboard"]


def salvar_permissoes_abas_neon(login, abas_permitidas):
    """Salva as abas permitidas para um usuário"""
    try:
        engine = get_engine()
        if engine is None:
            return False
        
        from sqlalchemy import text
        abas_str = ','.join(abas_permitidas) if abas_permitidas else None
        with engine.begin() as conn:
            conn.execute(
                text("UPDATE usuarios SET abas_acesso = %(abas)s WHERE login = %(login)s"),
                {'abas': abas_str, 'login': login}
            )
        return True
    except Exception as e:
        logging.warning(f"Erro ao salvar permissões de abas: {e}")
        return False


PERFIS_DISPONIVEIS = {
    "Master (Acesso técnico completo)": "master",
    "Técnico (Acesso irrestrito)": "tecnico",
    "Gestão (Tudo exceto Usuários)": "admin",
    "Secretaria": "secretaria",
    "Controle de Estoque": "controle_estoque",
    "Voluntário": "voluntario"
}


def obter_abas_padrao_por_perfil(perfil):
    perfil = (perfil or '').lower()
    opcoes_base = [
        "Dashboard",
        "Despensa",
        "Famílias",
        "Agendamentos",
        "Parceiros",
        "Voluntários",
        "Histórico",
        "Modo SOS",
        "Mapa Famílias",
        "Relatórios"
    ]

    if perfil in ("master", "tecnico"):
        return opcoes_base + ["Usuários"]
    if perfil == "admin":
        return opcoes_base
    if perfil == "secretaria":
        return [
            "Dashboard",
            "Despensa",
            "Famílias",
            "Agendamentos",
            "Parceiros",
            "Histórico",
            "Mapa Famílias",
            "Relatórios"
        ]
    if perfil == "controle_estoque":
        return ["Dashboard", "Despensa", "Relatórios"]
    if perfil == "voluntario":
        return ["Dashboard", "Famílias", "Agendamentos", "Mapa Famílias", "Histórico"]

    return opcoes_base


# ==========================================
# 3. INTEGRAÇÃO DE APIs (Georreferenciação)
# ==========================================
def buscar_endereco_viacep(cep):
    cep_limpo = ''.join(filter(str.isdigit, cep))
    if len(cep_limpo) != 8:
        return None, False
    try:
        url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
        resposta = requests.get(url, timeout=5)
        dados = resposta.json()
        if "erro" not in dados:
            return dados, True
    except:
        pass
    return None, False

def geocodificar_endereco(endereco_busca):
    url = "https://nominatim.openstreetmap.org/search"
    params = {'q': endereco_busca, 'format': 'json', 'limit': 1}
    headers = {'User-Agent': 'IgrejaAcaoSocialApp/1.0'}
    try:
        resposta = requests.get(url, params=params, headers=headers, timeout=5)
        dados = resposta.json()
        if dados:
            return float(dados[0]['lat']), float(dados[0]['lon'])
    except:
        pass
    return None, None 

# ==========================================
# 4. INICIALIZAÇÃO DO BANCO DE DADOS (MER)
# ==========================================
if 'db_catalogo' not in st.session_state:
    st.session_state.db_catalogo = pd.DataFrame([
        # Grãos e Cereais
        {'id_item': 1, 'nome': 'Arroz (5kg)', 'qtd_por_cesta': 1, 'categoria': 'Cesta'},
        {'id_item': 2, 'nome': 'Feijão (1kg)', 'qtd_por_cesta': 2, 'categoria': 'Cesta'},
        {'id_item': 3, 'nome': 'Macarrão (500g)', 'qtd_por_cesta': 2, 'categoria': 'Cesta'},
        {'id_item': 4, 'nome': 'Farinha de Trigo (1kg)', 'qtd_por_cesta': 1, 'categoria': 'Cesta'},
        
        # Óleos e Condimentos
        {'id_item': 5, 'nome': 'Óleo de Soja (900ml)', 'qtd_por_cesta': 1, 'categoria': 'Cesta'},
        {'id_item': 6, 'nome': 'Sal (1kg)', 'qtd_por_cesta': 1, 'categoria': 'Cesta'},
        {'id_item': 7, 'nome': 'Açúcar (1kg)', 'qtd_por_cesta': 1, 'categoria': 'Cesta'},
        
        # Laticínios e Proteínas
        {'id_item': 8, 'nome': 'Leite em Pó (400g)', 'qtd_por_cesta': 1, 'categoria': 'Cesta'},
        {'id_item': 9, 'nome': 'Ovo (dúzia)', 'qtd_por_cesta': 1, 'categoria': 'Cesta'},
        {'id_item': 10, 'nome': 'Sardinha em Lata (120g)', 'qtd_por_cesta': 1, 'categoria': 'Cesta'},
        
        # Frutas e Vegetais
        {'id_item': 11, 'nome': 'Batata-doce (kg)', 'qtd_por_cesta': 1, 'categoria': 'Cesta'},
        {'id_item': 12, 'nome': 'Cebola (kg)', 'qtd_por_cesta': 1, 'categoria': 'Cesta'},
        
        # Bebidas
        {'id_item': 13, 'nome': 'Café (500g)', 'qtd_por_cesta': 1, 'categoria': 'Cesta'},
        {'id_item': 14, 'nome': 'Achocolatado (400g)', 'qtd_por_cesta': 1, 'categoria': 'Cesta'},
        
        # Produtos de Higiene/Limpeza
        {'id_item': 15, 'nome': 'Sabão em Pó (500g)', 'qtd_por_cesta': 1, 'categoria': 'Cesta'},
        {'id_item': 16, 'nome': 'Desinfetante (1L)', 'qtd_por_cesta': 1, 'categoria': 'Cesta'},
        {'id_item': 17, 'nome': 'Sabonete (unidade)', 'qtd_por_cesta': 1, 'categoria': 'Cesta'},
    ])

if 'db_lotes' not in st.session_state:
    st.session_state.db_lotes = pd.DataFrame([
        # Grãos - Arroz
        {'id_lote': 1, 'id_item': 1, 'nome_item': 'Arroz (5kg)', 'quantidade': 25, 'vencimento': datetime.date(2026, 12, 1)},
        
        # Grãos - Feijão
        {'id_lote': 2, 'id_item': 2, 'nome_item': 'Feijão (1kg)', 'quantidade': 30, 'vencimento': datetime.date(2026, 8, 15)},
        {'id_lote': 3, 'id_item': 2, 'nome_item': 'Feijão (1kg)', 'quantidade': 15, 'vencimento': datetime.date(2026, 9, 20)},
        
        # Macarrão
        {'id_lote': 4, 'id_item': 3, 'nome_item': 'Macarrão (500g)', 'quantidade': 40, 'vencimento': datetime.date(2026, 11, 15)},
        
        # Farinha
        {'id_lote': 5, 'id_item': 4, 'nome_item': 'Farinha de Trigo (1kg)', 'quantidade': 20, 'vencimento': datetime.date(2026, 10, 10)},
        
        # Óleo
        {'id_lote': 6, 'id_item': 5, 'nome_item': 'Óleo de Soja (900ml)', 'quantidade': 35, 'vencimento': datetime.date(2026, 3, 20)},
        
        # Sal
        {'id_lote': 7, 'id_item': 6, 'nome_item': 'Sal (1kg)', 'quantidade': 50, 'vencimento': datetime.date(2027, 6, 15)},
        
        # Açúcar
        {'id_lote': 8, 'id_item': 7, 'nome_item': 'Açúcar (1kg)', 'quantidade': 30, 'vencimento': datetime.date(2026, 7, 30)},
        
        # Leite em Pó
        {'id_lote': 9, 'id_item': 8, 'nome_item': 'Leite em Pó (400g)', 'quantidade': 18, 'vencimento': datetime.date(2026, 5, 15)},
        
        # Ovos
        {'id_lote': 10, 'id_item': 9, 'nome_item': 'Ovo (dúzia)', 'quantidade': 12, 'vencimento': datetime.date(2026, 4, 30)},
        
        # Sardinha
        {'id_lote': 11, 'id_item': 10, 'nome_item': 'Sardinha em Lata (120g)', 'quantidade': 25, 'vencimento': datetime.date(2026, 9, 10)},
        
        # Batata-doce
        {'id_lote': 12, 'id_item': 11, 'nome_item': 'Batata-doce (kg)', 'quantidade': 40, 'vencimento': datetime.date(2026, 5, 20)},
        
        # Cebola
        {'id_lote': 13, 'id_item': 12, 'nome_item': 'Cebola (kg)', 'quantidade': 35, 'vencimento': datetime.date(2026, 6, 10)},
        
        # Café
        {'id_lote': 14, 'id_item': 13, 'nome_item': 'Café (500g)', 'quantidade': 20, 'vencimento': datetime.date(2026, 12, 15)},
        
        # Achocolatado
        {'id_lote': 15, 'id_item': 14, 'nome_item': 'Achocolatado (400g)', 'quantidade': 15, 'vencimento': datetime.date(2026, 8, 20)},
        
        # Sabão em Pó
        {'id_lote': 16, 'id_item': 15, 'nome_item': 'Sabão em Pó (500g)', 'quantidade': 22, 'vencimento': datetime.date(2026, 10, 25)},
        
        # Desinfetante
        {'id_lote': 17, 'id_item': 16, 'nome_item': 'Desinfetante (1L)', 'quantidade': 18, 'vencimento': datetime.date(2026, 9, 5)},
        
        # Sabonete
        {'id_lote': 18, 'id_item': 17, 'nome_item': 'Sabonete (unidade)', 'quantidade': 48, 'vencimento': datetime.date(2026, 11, 30)},
    ])

if 'db_familias' not in st.session_state:
    st.session_state.db_familias = pd.DataFrame([
        {
            'id_familia': 1, 'nome': 'Maria de Fátima', 'dependentes': 3, 'prioridade': 'Alta',
            'telefone': '(32) 98888-1234', 'atendimento_tipo': 'Contínuo',
            'cep': '36010001', 'endereco': 'Av. Barão do Rio Branco, 100 - Centro, Juiz de Fora/MG',
            'lat': -21.7611, 'lon': -43.3444,
            'igreja': 'Igreja Batista Central', 'pastor': 'Pr. Carlos',
            'ultima_entrega': None,
            'data_cadastro': datetime.date(2026, 5, 1)
        }
    ])

if 'db_entregas' not in st.session_state:
    st.session_state.db_entregas = pd.DataFrame(columns=['id_entrega', 'nome_familia', 'data', 'tipo'])

if 'db_agendamentos' not in st.session_state:
    st.session_state.db_agendamentos = pd.DataFrame(columns=[
        'id_agendamento', 'id_familia', 'nome_familia', 'data_agendada', 'hora_agendada',
        'tipo_entrega', 'voluntario', 'observacoes', 'status', 'data_criacao'
    ])

if 'db_locais_acolhimento' not in st.session_state:
    st.session_state.db_locais_acolhimento = pd.DataFrame([
        {'id_local': 1, 'nome': 'Salão Principal da Igreja', 'tipo': 'Igreja', 'capacidade': 30, 'cep': '36010001', 'endereco': 'Sede', 'lat': -21.7600, 'lon': -43.3400}
    ])

if 'db_pessoas_abrigadas' not in st.session_state:
    st.session_state.db_pessoas_abrigadas = pd.DataFrame(columns=['id_acolhido', 'id_local', 'nome_responsavel', 'qtd_pessoas', 'cep_origem', 'endereco_origem', 'lat_origem', 'lon_origem', 'data_entrada'])

if 'db_voluntarios' not in st.session_state:
    st.session_state.db_voluntarios = pd.DataFrame(columns=[
        'id_voluntario', 'nome', 'telefone', 'email', 'cep', 'endereco',
        'possui_veiculo', 'tipo_veiculo', 'dias_disponiveis', 'horario_inicio',
        'horario_fim', 'observacoes', 'data_cadastro', 'ativo'
    ])

if 'db_parceiros' not in st.session_state:
    st.session_state.db_parceiros = pd.DataFrame([
        {
            'id_parceiro': 1,
            'tipo_pessoa': 'Pessoa Física',
            'nome': 'Maria Aparecida',
            'documento': '000.000.000-00',
            'telefone': '(32) 98888-0000',
            'email': 'maria@igreja.org',
            'cep': '36010001',
            'endereco': 'Rua das Flores, 123',
            'contato_preferencial': 'E-mail',
            'alerta_mensal': True,
            'alerta_anual': True,
            'ultimo_agradecimento_mensal': None,
            'ultimo_agradecimento_anual': None,
            'itens_ajuda': 'Arroz, Feijão, Leite em Pó',
            'data_cadastro': datetime.date.today(),
            'ativo': True
        }
    ])

if 'entrega_ativa_familia' not in st.session_state:
    st.session_state.entrega_ativa_familia = None

if 'db_sos_whatsapp' not in st.session_state:
    st.session_state.db_sos_whatsapp = pd.DataFrame([
        {
            'id_msg': 1, 'telefone': '(32) 98888-1234', 'nome': 'Ana Souza', 
            'necessidade': 'Abrigo', 'pessoas': 4, 'cep': '36010001', 
            'status': 'Pendente', 'data_hora': datetime.datetime.now() - datetime.timedelta(minutes=5)
        },
        {
            'id_msg': 2, 'telefone': '(32) 97777-5678', 'nome': 'Carlos Dias', 
            'necessidade': 'Itens (Água/Marmita)', 'pessoas': 1, 'cep': '36020000', 
            'status': 'Pendente', 'data_hora': datetime.datetime.now() - datetime.timedelta(minutes=2)
        }
    ])

# ==========================================
# 5. LÓGICA DE NEGÓCIO
# ==========================================
def calcular_cestas_possiveis():
    cestas_possiveis = 9999
    for _, item in st.session_state.db_catalogo.iterrows():
        qtd_estoque = st.session_state.db_lotes[st.session_state.db_lotes['id_item'] == item['id_item']]['quantidade'].sum()
        qtd_necessaria = item['qtd_por_cesta']
        if qtd_necessaria > 0:
            capacidade_deste_item = qtd_estoque // qtd_necessaria
            if capacidade_deste_item < cestas_possiveis:
                cestas_possiveis = capacidade_deste_item
    return cestas_possiveis if cestas_possiveis != 9999 else 0

def excluir_familia_manual(id_familia):
    st.session_state.db_familias = st.session_state.db_familias[st.session_state.db_familias['id_familia'] != id_familia].reset_index(drop=True)
    excluir_familia_neon(id_familia)


def alocar_cesta_peps(id_familia):
    if calcular_cestas_possiveis() < 1:
        return False, "Não há itens suficientes para formar uma cesta completa."
    
    nome_familia = st.session_state.db_familias[st.session_state.db_familias['id_familia'] == id_familia]['nome'].values[0]

    for _, item in st.session_state.db_catalogo.iterrows():
        qtd_pendente = item['qtd_por_cesta']
        lotes = st.session_state.db_lotes[(st.session_state.db_lotes['id_item'] == item['id_item']) & (st.session_state.db_lotes['quantidade'] > 0)].sort_values(by='vencimento')
        for idx, lote in lotes.iterrows():
            if qtd_pendente <= 0: break
            qtd_a_retirar = min(lote['quantidade'], qtd_pendente)
            st.session_state.db_lotes.at[idx, 'quantidade'] -= qtd_a_retirar
            qtd_pendente -= qtd_a_retirar
            
    nova_entrega = {
        'id_entrega': len(st.session_state.db_entregas)+1,
        'id_familia': id_familia,
        'nome_familia': nome_familia,
        'data': datetime.date.today(),
        'tipo': 'Cesta Padrão'
    }
    st.session_state.db_entregas = pd.concat([st.session_state.db_entregas, pd.DataFrame([nova_entrega])], ignore_index=True)
    
    # Salva também no Neon
    salvar_entrega_neon(nova_entrega)
    
    excluir_familia_manual(id_familia)
    refresh_estoque_neon(force=True)
    return True, f"Cesta entregue para {nome_familia}. Família removida da fila de espera!"

def dar_baixa_avulsa_peps(id_item, qtd_desejada):
    lotes = st.session_state.db_lotes[(st.session_state.db_lotes['id_item'] == id_item) & (st.session_state.db_lotes['quantidade'] > 0)].sort_values(by='vencimento')
    total_disponivel = lotes['quantidade'].sum()
    if total_disponivel < qtd_desejada:
        return False, f"Estoque insuficiente! Temos apenas {total_disponivel} unidades."
    qtd_pendente = qtd_desejada
    for idx, lote in lotes.iterrows():
        if qtd_pendente <= 0: break
        qtd_a_retirar = min(lote['quantidade'], qtd_pendente)
        st.session_state.db_lotes.at[idx, 'quantidade'] -= qtd_a_retirar
        qtd_pendente -= qtd_a_retirar
    return True, "Baixa registrada no estoque real."


def criar_agendamento_entrega(dados_agendamento):
    dados = dados_agendamento.copy()
    dados['id_agendamento'] = len(st.session_state.db_agendamentos) + 1
    dados['status'] = 'Agendado'
    dados['data_criacao'] = datetime.datetime.now()
    st.session_state.db_agendamentos = pd.concat([st.session_state.db_agendamentos, pd.DataFrame([dados])], ignore_index=True)
    return True


def montar_html_card_voluntario(vol):
    """Gera o HTML do card de voluntário com valores escapados para evitar quebra do layout."""
    nome = html.escape(str(vol.get('nome', '-')))
    telefone = html.escape(str(vol.get('telefone', '-')))
    email = html.escape(str(vol.get('email', '-')))
    endereco = html.escape(str(vol.get('endereco', '-')))
    observacoes = html.escape(str(vol.get('observacoes', '-')))
    dias = html.escape(str(vol.get('dias_disponiveis', '-')))
    horario_inicio = html.escape(str(vol.get('horario_inicio', '-')))
    horario_fim = html.escape(str(vol.get('horario_fim', '-')))
    tipo_veiculo = html.escape(str(vol.get('tipo_veiculo', '-')))

    if vol.get('possui_veiculo', False):
        tag_veiculo = f"<span class='badge badge-success'>🚗 {tipo_veiculo}</span>"
    else:
        tag_veiculo = "<span class='badge badge-info'>🚶 Sem veículo</span>"

    contato_html = f"  |  ✉️ {email}" if email != '-' else ""
    observacoes_html = f"<div style='font-size:12px; color:#6B7280; margin-top:4px;'>💬 {observacoes}</div>" if observacoes != '-' else ""

    return f"""
        <div class="bento-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
                <div>
                    <div class="title-modern" style="font-size: 18px; margin-bottom: 2px;">{nome}</div>
                    <div class="subtitle-modern">📞 {telefone}{contato_html}</div>
                    <div class="subtitle-modern">📍 {endereco}</div>
                    <div style="margin-top: 6px; font-size: 13px; color: #374151;">
                        📅 <b>Disponível:</b> {dias} &nbsp;|&nbsp; ⏰ {horario_inicio} às {horario_fim}
                    </div>
                    {observacoes_html}
                </div>
                <div>{tag_veiculo}</div>
            </div>
        </div>
    """


def concluir_agendamento_entrega(id_agendamento):
    linhas = st.session_state.db_agendamentos[st.session_state.db_agendamentos['id_agendamento'] == id_agendamento]
    if linhas.empty:
        return False
    linha = linhas.iloc[0]
    nova_entrega = {
        'id_entrega': len(st.session_state.db_entregas) + 1,
        'id_familia': linha['id_familia'],
        'nome_familia': linha['nome_familia'],
        'data': datetime.date.today(),
        'tipo': f"{linha['tipo_entrega']} - {linha.get('observacoes', '') or ''}".strip()
    }
    st.session_state.db_entregas = pd.concat([st.session_state.db_entregas, pd.DataFrame([nova_entrega])], ignore_index=True)
    salvar_entrega_neon(nova_entrega)
    st.session_state.db_agendamentos.loc[st.session_state.db_agendamentos['id_agendamento'] == id_agendamento, 'status'] = 'Concluído'
    return True


def cancelar_agendamento_entrega(id_agendamento):
    if id_agendamento in st.session_state.db_agendamentos['id_agendamento'].values:
        st.session_state.db_agendamentos.loc[st.session_state.db_agendamentos['id_agendamento'] == id_agendamento, 'status'] = 'Cancelado'
        return True
    return False


def renderizar_mapa_alto_contraste(df_mapa, zoom_level=12, estilo_selecionado="Escuro"):
    """
    Gera um mapa interativo com opções de visualização melhoradas.
    """
    df_mapa = df_mapa.dropna(subset=['lat', 'lon']).copy()
    if df_mapa.empty: return
    
    # Define o estilo do mapa com base na escolha
    map_styles = {
        "Claro": "carto-positron",       # Fundo branco
        "Escuro": "carto-dark-matter",   # Fundo preto
        "Estradas": "road"               # Mapa de ruas padrão
    }
    style_uri = map_styles.get(estilo_selecionado, "carto-dark-matter")

    # Conversão de Cores
    def hex_to_rgba(hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)] + [200]
        return [255, 0, 0, 200]
        
    df_mapa['color_rgba'] = df_mapa['color'].apply(hex_to_rgba)
    
    # Camada de Pontos (Scatterplot)
    camada = pdk.Layer(
        "ScatterplotLayer",
        data=df_mapa,
        get_position="[lon, lat]",
        get_color="color_rgba",
        get_radius=200,          # Raio fixo em metros
        get_line_color=[0, 0, 0], # Borda preta em volta da bolinha
        get_line_width=20,        # Espessura da borda
        pickable=True,
        filled=True,
        stroked=True,            # Ativa o contorno para contraste
        radius_min_pixels=8,     # Garante que o ponto nunca fique minúsculo
        radius_max_pixels=30
    )

    # Configuração da Câmera
    visao = pdk.ViewState(
        latitude=df_mapa['lat'].mean(),
        longitude=df_mapa['lon'].mean(),
        zoom=zoom_level,
        pitch=0 # Pitch 0 facilita a leitura da localização exata (visão superior)
    )

    # Renderiza o Deck
    mapa = pdk.Deck(
        map_style=style_uri, 
        layers=[camada],
        initial_view_state=visao,
        tooltip={
            "html": "<div style='color:#e2e8f0; background:#0f172a; padding:10px; border-radius:8px; border:1px solid #334155;'><b>{nome}</b><br>{endereco}</div>"
        }
    )

    st.pydeck_chart(mapa)

def gerar_html_impressao(df, titulo, subtitulo=""):
    """
    Gera um HTML limpo e formatado especificamente para impressão ou PDF.
    """
    # CSS para garantir que saia bonito no papel A4
    estilo = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
        body { font-family: 'Roboto', sans-serif; color: #e2e8f0; padding: 20px; background: #0f172a; }
        h1 { text-align: center; text-transform: uppercase; font-size: 18px; margin-bottom: 5px; color: #f8fafc; }
        h2 { text-align: center; font-size: 14px; font-weight: normal; margin-bottom: 30px; color: #cbd5e1; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 12px; }
        th { background-color: #f3f3f3; border: 1px solid #ccc; padding: 8px; text-align: left; font-weight: bold; }
        td { border: 1px solid #ccc; padding: 8px; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .footer { margin-top: 40px; font-size: 10px; text-align: right; border-top: 1px solid #ccc; padding-top: 10px; }
        .assinatura { margin-top: 50px; display: flex; justify-content: space-between; }
        .linha-ass { border-top: 1px solid #000; width: 40%; text-align: center; padding-top: 5px; font-size: 12px; }
        
        /* Oculta elementos do Streamlit na hora de imprimir se o CSS global vazar */
        @media print {
            .stApp, header, footer, .stButton { display: none; }
            body { visibility: visible; }
        }
    </style>
    """
    
    # Monta a tabela HTML
    tabela_html = df.to_html(index=False, border=0, justify='left')
    
    html_final = f"""
    <html>
    <head>{estilo}</head>
    <body>
        <h1>{titulo}</h1>
        <h2>{subtitulo}</h2>
        {tabela_html}
        
        <div class="assinatura">
            <div class="linha-ass">Responsável pela Ação Social</div>
            <div class="linha-ass">Pastor / Liderança</div>
        </div>

        <div class="footer">
            Gerado pelo Sistema Gestão Solidária em {datetime.datetime.now().strftime('%d/%m/%Y às %H:%M')}.
        </div>
    </body>
    </html>
    """
    return html_final
# ==========================================
# 6. APLICAÇÃO PRINCIPAL (Pós-Login)
# ==========================================
def main_app():
    refresh_estoque_neon()
    if st.session_state.force_password_change:
        st.markdown("### Primeiro acesso: altere sua senha")
        with st.form("form_forcar_alterar_senha"):
            senha_atual = st.text_input("Senha Atual", type="password")
            senha_nova = st.text_input("Nova Senha", type="password")
            senha_confirmada = st.text_input("Confirmar Nova Senha", type="password")
            if st.form_submit_button("Alterar Senha", use_container_width=True):
                if not senha_atual or not senha_nova or not senha_confirmada:
                    st.error("Preencha todos os campos.")
                elif senha_nova != senha_confirmada:
                    st.error("As novas senhas não conferem.")
                elif len(senha_nova) < 6:
                    st.error("A nova senha deve ter pelo menos 6 caracteres.")
                elif not validar_usuario(st.session_state.user_login, senha_atual):
                    st.error("Senha atual incorreta.")
                elif alterar_senha_neon(st.session_state.user_login, senha_nova):
                    st.success("✅ Senha alterada com sucesso. Agora você pode acessar o sistema.")
                    st.session_state.force_password_change = False
                    st.rerun()
                else:
                    st.error("Erro ao alterar senha. Tente novamente.")
        st.stop()

    # --- Sidebar de Navegação ---
    with st.sidebar:
        nome_exibido = st.session_state.current_user or 'Usuário'
        perfil_exibido = st.session_state.user_role or 'visitante'
        st.markdown(f"### Olá, {nome_exibido} 👋")
        st.markdown(f"<span class='badge badge-info'>{perfil_exibido.title()}</span>", unsafe_allow_html=True)
        st.markdown("---")

        # OPÇÃO: Alterar Senha
        with st.expander("🔐 Alterar Senha"):
            with st.form("form_alterar_senha"):
                senha_atual = st.text_input("Senha Atual", type="password", key="atual")
                senha_nova = st.text_input("Nova Senha", type="password", key="nova")
                senha_confirmada = st.text_input("Confirmar Nova Senha", type="password", key="confirmar")
                
                if st.form_submit_button("Alterar Senha", use_container_width=True):
                    # Validar senha atual
                    usuario_info = validar_usuario(st.session_state.user_login, senha_atual)
                    if usuario_info:
                        if senha_nova != senha_confirmada:
                            st.error("As novas senhas não conferem.")
                        elif len(senha_nova) < 6:
                            st.error("A nova senha deve ter pelo menos 6 caracteres.")
                        elif alterar_senha_neon(st.session_state.user_login, senha_nova):
                            st.success("✅ Senha alterada com sucesso!")
                        else:
                            st.error("Erro ao alterar senha. Tente novamente.")
                    else:
                        st.error("Senha atual incorreta.")
        
        st.markdown("---")

        opcoes_menu = obter_abas_permitidas(st.session_state.user_login, st.session_state.user_role)

        if 'menu_opcao' not in st.session_state or st.session_state.menu_opcao not in opcoes_menu:
            st.session_state.menu_opcao = opcoes_menu[0]

        menu_opcao = st.radio(
            "Navegação",
            opcoes_menu,
            index=opcoes_menu.index(st.session_state.menu_opcao),
            label_visibility="collapsed",
            key="menu_opcao"
        )

        if menu_opcao not in opcoes_menu:
            st.error("Aba não autorizada para o seu perfil.")
            st.stop()

        st.markdown("---")
        st.info(f"📅 {datetime.date.today().strftime('%d/%m/%Y')}")
        if st.button("🚪 Sair do Sistema", use_container_width=True):
            logout()

    # --- Conteúdo Principal ---
    st.markdown(f"<h2 style='font-weight: 800; color: var(--text-main); margin-bottom: 20px;'>{menu_opcao}</h2>", unsafe_allow_html=True)

    if menu_opcao == "Dashboard":
        col1, col2 = st.columns(2)
        with col1:
            cestas = calcular_cestas_possiveis()
            st.markdown(f"""
                <div class="bento-card">
                    <div class="subtitle-modern">Kits Prontos para Montagem</div>
                    <div class="text-gradient">{cestas}</div>
                    <div class="subtitle-modern">Cestas completas com base no estoque atual.</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            hoje = datetime.date.today()
            lotes_ativos = st.session_state.db_lotes[st.session_state.db_lotes['quantidade'] > 0]
            vencendo = lotes_ativos[lotes_ativos['vencimento'] <= hoje + datetime.timedelta(days=30)]
            borda_alerta = "border: 2px solid #FCA5A5;" if not vencendo.empty else ""
            cor_numero = "#DC2626" if not vencendo.empty else "#4D7C0F"
            st.markdown(f"""
                <div class="bento-card" style="{borda_alerta}">
                    <div class="subtitle-modern">Alerta de Validade (PEPS)</div>
                    <div class="title-modern" style="font-size: 48px; color: {cor_numero};">{len(vencendo)}</div>
                    <div class="subtitle-modern">Lotes a vencer nos próximos 30 dias.</div>
                </div>
            """, unsafe_allow_html=True)

    elif menu_opcao == "Despensa":
        refresh_estoque_neon()

        if st.button("🔄 Atualizar Estoque", use_container_width=False):
            refresh_estoque_neon(force=True)
            st.success("Estoque sincronizado com o banco de dados.")
            st.rerun()

        col_entrada, col_catalogo = st.columns([2, 1])
        
        with col_catalogo:
            st.markdown("<div class='title-modern'>Novo Tipo de Item</div>", unsafe_allow_html=True)
            with st.form("form_novo_catalogo", clear_on_submit=True):
                novo_nome = st.text_input("Nome")
                tipo_item = st.radio("Regra:", ["Item Avulso/Extra", "Obrigatório na Cesta"])
                qtd_cesta = st.number_input("Qtd por Cesta", min_value=1, value=1) if "Obrigatório" in tipo_item else 0
                categoria = "Cesta" if "Obrigatório" in tipo_item else "Avulso"
                
                if st.form_submit_button("Adicionar", type="primary", use_container_width=True):
                    if novo_nome:
                        novo_id = st.session_state.db_catalogo['id_item'].max() + 1 if not st.session_state.db_catalogo.empty else 1
                        novo_item = {
                            'id_item': novo_id,
                            'nome': novo_nome,
                            'qtd_por_cesta': qtd_cesta,
                            'categoria': categoria
                        }
                        st.session_state.db_catalogo = pd.concat([st.session_state.db_catalogo, pd.DataFrame([novo_item])], ignore_index=True)
                        if salvar_item_catalogo_neon(novo_item):
                            refresh_estoque_neon(force=True)
                        st.success("Adicionado!")
                        st.rerun()

        with col_entrada:
            st.markdown("<div class='title-modern'>Registrar Entrada</div>", unsafe_allow_html=True)
            with st.form("form_entrada", clear_on_submit=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                item_selecionado = c1.selectbox("Produto", st.session_state.db_catalogo['nome'])
                qtd = c2.number_input("Qtd", min_value=1)
                venc = c3.date_input("Vencimento")
                
                if st.form_submit_button("Guardar Estoque", use_container_width=True):
                    id_item_escolhido = st.session_state.db_catalogo[st.session_state.db_catalogo['nome'] == item_selecionado]['id_item'].values[0]
                    novo_lote = {
                        'id_lote': len(st.session_state.db_lotes) + 1,
                        'id_item': id_item_escolhido,
                        'nome_item': item_selecionado,
                        'quantidade': qtd,
                        'vencimento': venc
                    }
                    st.session_state.db_lotes = pd.concat([st.session_state.db_lotes, pd.DataFrame([novo_lote])], ignore_index=True)
                    if salvar_lote_neon(novo_lote):
                        refresh_estoque_neon(force=True)
                    st.success("Registado!")
                    st.rerun()

        st.markdown("---")
        st.markdown("<div class='title-modern'>Estoque Físico Atual</div>", unsafe_allow_html=True)
        if not st.session_state.db_lotes.empty and st.session_state.db_lotes['quantidade'].sum() > 0:
            hoje = datetime.date.today()
            df_exibicao = pd.merge(st.session_state.db_lotes[st.session_state.db_lotes['quantidade'] > 0], st.session_state.db_catalogo, on='id_item')
            df_exibicao = df_exibicao.groupby(['id_item', 'nome'], as_index=False).agg(
                quantidade=('quantidade', 'sum'),
                vencimento_proximo=('vencimento', 'min'),
                vence_proximo=('vencimento', lambda s: (pd.to_datetime(s) <= pd.Timestamp(hoje + datetime.timedelta(days=30))).any())
            )
            df_exibicao['Vence em'] = pd.to_datetime(df_exibicao['vencimento_proximo']).dt.strftime('%d/%m/%Y')
            df_exibicao['Alerta'] = df_exibicao['vence_proximo'].apply(lambda x: '⚠️ Vence em até 30 dias' if x else 'OK')
            df_exibicao.rename(columns={'nome': 'Produto', 'quantidade': 'Qtd Disponível'}, inplace=True)
            st.dataframe(df_exibicao[['Produto', 'Qtd Disponível', 'Vence em', 'Alerta']], use_container_width=True, hide_index=True)
        else:
            st.info("A despensa está vazia.")

    elif menu_opcao == "Famílias":
        c1, c2 = st.columns([3, 1])
        c1.markdown("<div class='title-modern'>Fila de Espera</div>", unsafe_allow_html=True)
        if st.button("🔄 Atualizar Famílias", use_container_width=False):
            refresh_estoque_neon(force=True)
            st.success("Dados sincronizados com o banco de dados.")
            st.rerun()
        
        with st.expander("➕ Cadastrar Nova Família", expanded=True):
            with st.form("form_familia", clear_on_submit=True):
                st.markdown("##### Dados Pessoais")
                nome = st.text_input("Nome do Responsável *")
                col_dep, col_prio = st.columns(2)
                dep = col_dep.number_input("Número de Dependentes", min_value=0)
                prio = col_prio.selectbox("Prioridade", ["Normal", "Alta (Urgência)"])
                
                st.markdown("##### Contato e Endereço")
                col_tel, col_cep = st.columns([1, 1])
                telefone = col_tel.text_input("Telefone de Contato *", placeholder="(32) 99999-0000")
                cep = col_cep.text_input("CEP (Somente números) *", max_chars=8)
                numero = st.text_input("Número e Complemento *")

                st.markdown("##### Tipo de Atendimento")
                tipo_atendimento = st.selectbox("Atendimento", ["Contínuo", "Esporádico"])

                # --- NOVOS CAMPOS PARA CORREÇÃO DO MAPA ---
                st.markdown("##### 📍 Coordenadas (Opcional - Use se o mapa automático falhar)")
                st.caption("Dica: No Google Maps, clique com o botão direito no local e copie os números (Ex: -23.55, -46.63)")
                c_lat, c_lon = st.columns(2)
                lat_manual = c_lat.text_input("Latitude", placeholder="Ex: -21.7611")
                lon_manual = c_lon.text_input("Longitude", placeholder="Ex: -43.3444")
                
                st.markdown("##### Dados Eclesiásticos")
                col_igreja, col_pastor = st.columns(2)
                igreja = col_igreja.text_input("Nome da Igreja")
                pastor = col_pastor.text_input("Nome do Pastor")
                
                if st.form_submit_button("Cadastrar Família", type="primary"):
                    if nome and cep and numero and telefone:
                        lat, lon = None, None
                        endereco_display = "Endereço em processamento"

                        # 1. Tenta usar coordenadas manuais se preenchidas
                        if lat_manual and lon_manual:
                            try:
                                lat = float(lat_manual.replace(',', '.'))
                                lon = float(lon_manual.replace(',', '.'))
                                # Busca o endereço pelo CEP apenas para texto
                                dados_cep, _ = buscar_endereco_viacep(cep)
                                if dados_cep:
                                    endereco_display = f"{dados_cep.get('logradouro','')}, {numero} - {dados_cep.get('bairro','')}"
                                else:
                                    endereco_display = f"CEP {cep}, {numero}"
                            except:
                                st.warning("⚠️ Coordenadas manuais inválidas. Tentando busca automática...")

                        # 2. Se não tiver manual, tenta o automático
                        if lat is None:
                            with st.spinner("Buscando endereço no satélite..."):
                                dados_cep, sucesso_cep = buscar_endereco_viacep(cep)
                                if sucesso_cep:
                                    endereco_display = f"{dados_cep.get('logradouro','')}, {numero} - {dados_cep.get('bairro','')}"
                                    # Tenta achar Latitude/Longitude
                                    lat, lon = geocodificar_endereco(f"{dados_cep.get('logradouro','')}, {numero}, {dados_cep.get('localidade','')}, Brasil")
                        
                        # 3. Salva no Banco de Dados
                        nova_fam = {
                            'id_familia': len(st.session_state.db_familias)+1,
                            'nome': nome,
                            'dependentes': dep,
                            'prioridade': prio.split(" ")[0],
                            'telefone': telefone,
                            'atendimento_tipo': tipo_atendimento,
                            'cep': cep,
                            'endereco': endereco_display,
                            'lat': lat,
                            'lon': lon, # Pode ser None se falhar
                            'igreja': igreja if igreja else 'Não informado',
                            'pastor': pastor if pastor else '-',
                            'ultima_entrega': None,
                            'data_cadastro': datetime.date.today()
                        }
                        st.session_state.db_familias = pd.concat([st.session_state.db_familias, pd.DataFrame([nova_fam])], ignore_index=True)
                        
                        # Salva também no Neon
                        salvar_familia_neon(nova_fam)
                        
                        # 4. Feedback ao Usuário
                        if lat is not None:
                            st.success(f"✅ Cadastro realizado e localizado no mapa!")
                        else:
                            st.warning(f"⚠️ Família cadastrada, mas **o endereço não foi encontrado no mapa**. Por favor, edite ou cadastre novamente inserindo a Latitude e Longitude manualmente.")
                        
                        st.rerun()
                    else:
                        st.error("Preencha os campos obrigatórios (*).")

        # LISTAGEM DAS FAMÍLIAS
        if not st.session_state.db_familias.empty:
            for _, fam in st.session_state.db_familias.iterrows():
                tag_prio = f"<span class='pill-tag-alert'>Prioridade Alta</span>" if fam['prioridade'] == 'Alta' else f"<span class='pill-tag-neutral'>Normal</span>"
                
                # Verifica se está no mapa
                status_mapa = "📍 No Mapa" if pd.notnull(fam['lat']) else "⚠️ <b>Sem Mapa</b> (Exclua e cadastre com Lat/Lon)"
                
                data_cadastro_text = ''
                if pd.notnull(fam.get('data_cadastro')):
                    data_cadastro_text = pd.to_datetime(fam['data_cadastro']).strftime('%d/%m/%Y')
                st.markdown(f"""
                    <div class="bento-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <div class="title-modern" style="font-size: 18px;">{fam['nome']}</div>
                                <div class="subtitle-modern">
                                    👥 {fam['dependentes']} Dep. | {fam['endereco']}
                                </div>
                                <div class="subtitle-modern" style="margin-top: 8px; font-size: 13px; color: #cbd5e1;">
                                    ☎️ {fam.get('telefone','-')} | Atendimento: {fam.get('atendimento_tipo','-')}
                                </div>
                                <div style="font-size: 12px; margin-top: 5px; color: #94a3b8;">{status_mapa}</div>
                                <div style="font-size: 12px; color: #94a3b8;">{('Cadastro: ' + data_cadastro_text) if data_cadastro_text else ''}</div>
                            </div>
                            {tag_prio}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button(f"📦 Entregar", key=f"ent_{fam['id_familia']}", use_container_width=True):
                        st.session_state.entrega_ativa_familia = fam['id_familia']
                        st.rerun()
                with c_btn2:
                    if st.button(f"🗑️ Excluir", key=f"exc_{fam['id_familia']}", use_container_width=True):
                        excluir_familia_manual(fam['id_familia'])
                        st.rerun()

                # PAINEL DE ENTREGA EXPANDIDO
                if st.session_state.entrega_ativa_familia == fam['id_familia']:
                    with st.container():
                        st.markdown(f"""
                            <div style="background: #111827; border: 2px solid var(--primary); border-radius: 12px; padding: 20px; margin: 8px 0;">
                                <h4 style="color: #bfdbfe; margin: 0 0 4px 0;">📦 Painel de Entrega — {fam['nome']}</h4>
                                <p style="color: #93c5fd; font-size: 13px; margin: 0;">Escolha o tipo de entrega abaixo</p>
                            </div>
                        """, unsafe_allow_html=True)

                        # --- Calcula estoque disponível ---
                        df_estoque = pd.merge(
                            st.session_state.db_lotes[st.session_state.db_lotes['quantidade'] > 0],
                            st.session_state.db_catalogo,
                            on='id_item'
                        ).groupby(['id_item', 'nome', 'qtd_por_cesta']).agg({'quantidade': 'sum'}).reset_index()
                        df_estoque.columns = ['id_item', 'nome', 'qtd_por_cesta', 'qtd_total']

                        cestas_disp = calcular_cestas_possiveis()

                        tab_cesta, tab_avulso = st.tabs(["🧺 Cesta Básica", "🛒 Itens Avulsos"])

                        # ---- ABA CESTA ----
                        with tab_cesta:
                            if cestas_disp >= 1:
                                st.success(f"✅ Estoque suficiente para **{cestas_disp} cesta(s)**.")
                                st.markdown("**Composição da cesta que será entregue:**")
                                itens_cesta = df_estoque[df_estoque['qtd_por_cesta'] > 0][['nome', 'qtd_por_cesta', 'qtd_total']].copy()
                                itens_cesta.columns = ['Item', 'Qtd na Cesta', 'Disponível em Estoque']
                                st.dataframe(itens_cesta, use_container_width=True, hide_index=True)
                                col_conf, col_can = st.columns(2)
                                with col_conf:
                                    if st.button("✅ Confirmar Entrega da Cesta", key=f"conf_cesta_{fam['id_familia']}", type="primary", use_container_width=True):
                                        suc, msg = alocar_cesta_peps(fam['id_familia'])
                                        st.session_state.entrega_ativa_familia = None
                                        if suc:
                                            st.success(msg)
                                        else:
                                            st.error(msg)
                                        st.rerun()
                                with col_can:
                                    if st.button("❌ Cancelar", key=f"can_cesta_{fam['id_familia']}", use_container_width=True):
                                        st.session_state.entrega_ativa_familia = None
                                        st.rerun()
                            else:
                                st.error("❌ Estoque insuficiente para montar uma cesta completa.")
                                st.caption("Itens faltantes para completar a cesta:")
                                for _, item in st.session_state.db_catalogo.iterrows():
                                    if item['qtd_por_cesta'] > 0:
                                        disp = st.session_state.db_lotes[st.session_state.db_lotes['id_item'] == item['id_item']]['quantidade'].sum()
                                        if disp < item['qtd_por_cesta']:
                                            st.markdown(f"- **{item['nome']}**: precisa {item['qtd_por_cesta']}, tem {int(disp)}")
                                if st.button("Fechar", key=f"fecha_cesta_{fam['id_familia']}", use_container_width=True):
                                    st.session_state.entrega_ativa_familia = None
                                    st.rerun()

                        # ---- ABA AVULSO ----
                        with tab_avulso:
                            if df_estoque.empty:
                                st.warning("Nenhum item disponível no estoque.")
                            else:
                                st.markdown("**Selecione os itens e quantidades:**")
                                selecoes_avulsas = {}
                                for _, item_row in df_estoque.iterrows():
                                    col_nome, col_qtd = st.columns([3, 1])
                                    with col_nome:
                                        st.markdown(f"**{item_row['nome']}**  \n<small style='color:#6B7280'>Disponível: {int(item_row['qtd_total'])} un.</small>", unsafe_allow_html=True)
                                    with col_qtd:
                                        qtd_sel = st.number_input(
                                            "Qtd",
                                            min_value=0,
                                            max_value=int(item_row['qtd_total']),
                                            value=0,
                                            key=f"avulso_{fam['id_familia']}_{item_row['id_item']}",
                                            label_visibility="collapsed"
                                        )
                                    if qtd_sel > 0:
                                        selecoes_avulsas[item_row['id_item']] = {'nome': item_row['nome'], 'qtd': qtd_sel}

                                col_av1, col_av2 = st.columns(2)
                                with col_av1:
                                    if st.button("✅ Confirmar Itens Avulsos", key=f"conf_avulso_{fam['id_familia']}", type="primary", use_container_width=True):
                                        if not selecoes_avulsas:
                                            st.warning("Selecione ao menos um item com quantidade maior que zero.")
                                        else:
                                            erros = []
                                            itens_entregues = []
                                            for id_it, dados_it in selecoes_avulsas.items():
                                                suc, msg = dar_baixa_avulsa_peps(id_it, dados_it['qtd'])
                                                if suc:
                                                    itens_entregues.append(f"{dados_it['qtd']}x {dados_it['nome']}")
                                                else:
                                                    erros.append(f"{dados_it['nome']}: {msg}")

                                            if erros:
                                                for e in erros:
                                                    st.error(e)
                                            else:
                                                descricao_itens = ", ".join(itens_entregues)
                                                nova_entrega = {
                                                    'id_entrega': len(st.session_state.db_entregas) + 1,
                                                    'id_familia': fam['id_familia'],
                                                    'nome_familia': fam['nome'],
                                                    'data': datetime.date.today(),
                                                    'tipo': f"Avulso: {descricao_itens}"
                                                }
                                                st.session_state.db_entregas = pd.concat(
                                                    [st.session_state.db_entregas, pd.DataFrame([nova_entrega])],
                                                    ignore_index=True
                                                )
                                                salvar_entrega_neon(nova_entrega)
                                                st.session_state.entrega_ativa_familia = None
                                                st.success(f"✅ Entrega registrada: {descricao_itens}")
                                                st.rerun()
                                with col_av2:
                                    if st.button("❌ Cancelar", key=f"can_avulso_{fam['id_familia']}", use_container_width=True):
                                        st.session_state.entrega_ativa_familia = None
                                        st.rerun()
        else:
            st.info("Nenhuma família cadastrada.")

    elif menu_opcao == "Agendamentos":
        st.markdown("<div class='title-modern'>Agendamentos de Entrega</div>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle-modern'>Agende a retirada ou entrega de itens e acompanhe o status de cada pedido.</p>", unsafe_allow_html=True)

        with st.expander("➕ Novo Agendamento", expanded=True):
            with st.form("form_agendamento", clear_on_submit=True):
                familia_selecionada = st.selectbox(
                    "Família",
                    options=st.session_state.db_familias['id_familia'].tolist() if not st.session_state.db_familias.empty else [],
                    format_func=lambda x: f"{st.session_state.db_familias[st.session_state.db_familias['id_familia'] == x]['nome'].iloc[0]}"
                    if not st.session_state.db_familias[st.session_state.db_familias['id_familia'] == x].empty else str(x)
                )
                data_agendada = st.date_input("Data da Entrega", value=datetime.date.today())
                hora_agendada = st.time_input("Horário da Entrega", value=datetime.time(9, 0))
                tipo_entrega = st.radio("Tipo de Entrega", ["Presencial na Igreja", "Residência"], horizontal=True)
                voluntario = st.text_input("Responsável/Voluntário (opcional)")
                observacoes = st.text_area("Observações", help="Use este campo para itens combinados ou observações especiais.")

                if st.form_submit_button("Agendar Entrega", type="primary", use_container_width=True):
                    if familia_selecionada and data_agendada:
                        familia = st.session_state.db_familias[st.session_state.db_familias['id_familia'] == familia_selecionada].iloc[0]
                        criar_agendamento_entrega({
                            'id_familia': familia_selecionada,
                            'nome_familia': familia['nome'],
                            'data_agendada': data_agendada,
                            'hora_agendada': hora_agendada.strftime('%H:%M'),
                            'tipo_entrega': tipo_entrega,
                            'voluntario': voluntario or '-',
                            'observacoes': observacoes or ''
                        })
                        st.success(f"✅ Entrega agendada para {familia['nome']} em {data_agendada.strftime('%d/%m/%Y')}.")
                        st.rerun()
                    else:
                        st.error("Selecione a família e a data da entrega.")

        st.markdown("---")
        if st.session_state.db_agendamentos.empty:
            st.info("Não há agendamentos registrados.")
        else:
            agendamentos_exibicao = st.session_state.db_agendamentos.copy()
            agendamentos_exibicao['data_agendada'] = pd.to_datetime(agendamentos_exibicao['data_agendada']).dt.strftime('%d/%m/%Y')
            agendamentos_exibicao['data_criacao'] = pd.to_datetime(agendamentos_exibicao['data_criacao']).dt.strftime('%d/%m/%Y %H:%M')
            st.dataframe(
                agendamentos_exibicao[['id_agendamento', 'nome_familia', 'data_agendada', 'hora_agendada', 'tipo_entrega', 'voluntario', 'status']],
                use_container_width=True,
                hide_index=True
            )

            for _, ag in st.session_state.db_agendamentos.sort_values(by=['data_agendada', 'hora_agendada']).iterrows():
                if ag['status'] == 'Agendado':
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**#{int(ag['id_agendamento'])} — {ag['nome_familia']}** — {ag['data_agendada']} às {ag['hora_agendada']} ({ag['tipo_entrega']})")
                        st.markdown(f"<small>{ag['observacoes'] or 'Sem observações'} | Voluntário: {ag['voluntario']}</small>", unsafe_allow_html=True)
                    with col2:
                        if st.button(f"Concluir", key=f"concluir_ag_{ag['id_agendamento']}", use_container_width=True):
                            concluir_agendamento_entrega(ag['id_agendamento'])
                            st.success("Agendamento concluído e registrado como entrega.")
                            st.rerun()
                        if st.button(f"Cancelar", key=f"cancelar_ag_{ag['id_agendamento']}", use_container_width=True):
                            cancelar_agendamento_entrega(ag['id_agendamento'])
                            st.warning("Agendamento cancelado.")
                            st.rerun()

    elif menu_opcao == "Parceiros":
        st.markdown("<div class='title-modern'>Cadastro de Parceiros</div>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle-modern'>Registre parceiros que ajudam a despensa e receba alertas de agradecimento.</p>", unsafe_allow_html=True)

        with st.expander("➕ Cadastrar Novo Parceiro", expanded=True):
            with st.form("form_parceiro", clear_on_submit=True):
                st.markdown("##### Dados do Parceiro")
                tipo_pessoa = st.radio("Tipo de Pessoa", ["Pessoa Física", "Pessoa Jurídica"], horizontal=True)
                nome_par = st.text_input("Nome / Razão Social *")
                documento = st.text_input("CPF / CNPJ")
                telefone_par = st.text_input("Telefone *", placeholder="(32) 99999-0000")
                email_par = st.text_input("E-mail")

                st.markdown("##### Endereço")
                cep_par = st.text_input("CEP", max_chars=8)
                endereco_par = st.text_area("Endereço completo")

                st.markdown("##### Preferências de Agradecimento")
                contato_preferencial = st.selectbox("Enviar agradecimento por", ["E-mail", "Correios", "Ambos"])
                alerta_mensal = st.checkbox("Alerta mensal", value=True)
                alerta_anual = st.checkbox("Alerta anual", value=False)
                itens_ajuda = st.text_area("Itens que costumam ajudar na despensa", help="Ex: arroz, feijão, óleo, leite em pó")

                if st.form_submit_button("Cadastrar Parceiro", type="primary"):
                    if nome_par and telefone_par:
                        novo_parceiro = {
                            'id_parceiro': len(st.session_state.db_parceiros) + 1,
                            'tipo_pessoa': tipo_pessoa,
                            'nome': nome_par,
                            'documento': documento,
                            'telefone': telefone_par,
                            'email': email_par,
                            'cep': cep_par,
                            'endereco': endereco_par,
                            'contato_preferencial': contato_preferencial,
                            'alerta_mensal': alerta_mensal,
                            'alerta_anual': alerta_anual,
                            'ultimo_agradecimento_mensal': None,
                            'ultimo_agradecimento_anual': None,
                            'itens_ajuda': itens_ajuda,
                            'data_cadastro': datetime.date.today(),
                            'ativo': True
                        }
                        st.session_state.db_parceiros = pd.concat([st.session_state.db_parceiros, pd.DataFrame([novo_parceiro])], ignore_index=True)
                        salvar_parceiro_neon(novo_parceiro)
                        st.success("✅ Parceiro cadastrado com sucesso.")
                        st.rerun()
                    else:
                        st.error("Preencha os campos obrigatórios.")

        if st.session_state.db_parceiros.empty:
            st.info("Nenhum parceiro registrado ainda.")
        else:
            hoje = datetime.date.today()
            for _, par in st.session_state.db_parceiros.iterrows():
                mensal_due = par['alerta_mensal'] and (pd.isna(par['ultimo_agradecimento_mensal']) or pd.to_datetime(par['ultimo_agradecimento_mensal']).date() <= hoje - datetime.timedelta(days=30))
                anual_due = par['alerta_anual'] and (pd.isna(par['ultimo_agradecimento_anual']) or pd.to_datetime(par['ultimo_agradecimento_anual']).date() <= hoje - datetime.timedelta(days=365))
                status_lista = []
                if mensal_due:
                    status_lista.append("Agradecimento mensal pendente")
                if anual_due:
                    status_lista.append("Agradecimento anual pendente")
                if not status_lista:
                    status_lista.append("Nenhum alerta pendente")

                data_cadastro_text = pd.to_datetime(par['data_cadastro']).strftime('%d/%m/%Y') if pd.notnull(par.get('data_cadastro')) else 'Não informado'
                st.markdown(f"""
                    <div class='bento-card'>
                        <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
                            <div>
                                <div class='title-modern' style='font-size: 18px;'>{par['nome']}</div>
                                <div class='subtitle-modern'>
                                    {par['tipo_pessoa']} | {par.get('contato_preferencial', '-')}
                                </div>
                                <div style='font-size: 13px; margin-top: 8px; color: #cbd5e1;'>
                                    ☎️ {par.get('telefone', '-')} | ✉️ {par.get('email', '-')}
                                </div>
                                <div style='font-size: 12px; color: #94a3b8; margin-top: 4px;'>Cadastro: {data_cadastro_text}</div>
                                <div style='font-size: 13px; margin-top: 8px; color: #e2e8f0;'>Itens: {par.get('itens_ajuda', '-')}</div>
                                <div style='font-size: 12px; margin-top: 8px; color: #facc15;'>{' • '.join(status_lista)}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    elif menu_opcao == "Usuários":
        st.markdown("<div class='title-modern'>Gerenciamento de Usuários</div>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle-modern'>Cadastre e gerencie perfis de acesso para o sistema.</p>", unsafe_allow_html=True)

        with st.expander("➕ Cadastrar Novo Usuário", expanded=True):
            with st.form("form_usuario", clear_on_submit=True):
                nome_novo = st.text_input("Nome Completo")
                login_novo = st.text_input("Login / Usuário")
                senha_nova = st.text_input("Senha", type="password")
                perfil_novo = st.selectbox("Perfil", list(PERFIS_DISPONIVEIS.keys()))
                ativo_novo = st.checkbox("Ativo", value=True)

                if st.form_submit_button("Cadastrar Usuário", type="primary", use_container_width=True):
                    if nome_novo and login_novo and senha_nova:
                        perfil_interno = PERFIS_DISPONIVEIS.get(perfil_novo, perfil_novo)
                        novo_usuario = {
                            'login': login_novo.lower().strip(),
                            'nome': nome_novo.strip(),
                            'senha': senha_nova,
                            'perfil': perfil_interno,
                            'ativo': ativo_novo
                        }
                        if salvar_usuario_neon(novo_usuario):
                            st.success("✅ Usuário cadastrado com sucesso.")
                        else:
                            st.error("Falha ao cadastrar usuário. Verifique se o login já existe.")
                        st.rerun()
                    else:
                        st.error("Preencha todos os campos obrigatórios.")

        st.markdown("---")
        st.markdown("### Usuários cadastrados")
        df_usuarios = carregar_usuarios_neon()
        if df_usuarios is not None and not df_usuarios.empty:
            st.dataframe(df_usuarios[['id_usuario', 'login', 'nome', 'perfil', 'ativo']], use_container_width=True, hide_index=True)
            for _, usuario in df_usuarios.iterrows():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{usuario['nome']}** (<code>{usuario['login']}</code>) — {usuario['perfil']} — {'Ativo' if usuario['ativo'] else 'Inativo'}")
                with col2:
                    if usuario['ativo']:
                        if st.button(f"Desativar", key=f"desativar_usuario_{usuario['id_usuario']}", use_container_width=True):
                            set_usuario_ativo_neon(usuario['id_usuario'], False)
                            st.success("Usuário desativado.")
                            st.rerun()
                    else:
                        if st.button(f"Ativar", key=f"ativar_usuario_{usuario['id_usuario']}", use_container_width=True):
                            set_usuario_ativo_neon(usuario['id_usuario'], True)
                            st.success("Usuário ativado.")
                            st.rerun()
        else:
            st.warning("Nenhum usuário cadastrado no sistema.")

        # --- GERENCIAR PERMISSÕES DE ABAS ---
        st.markdown("---")
        st.markdown("### 🔓 Controle de Acesso às Abas")
        st.markdown("<p class='subtitle-modern'>Customize quais abas cada usuário pode acessar (deixe em branco para usar as permissões padrão do perfil).</p>", unsafe_allow_html=True)
        
        df_usuarios = carregar_usuarios_neon()
        if df_usuarios is not None and not df_usuarios.empty:
            usuario_sel = st.selectbox(
                "Selecione um usuário para customizar acesso:",
                options=df_usuarios['login'].tolist(),
                format_func=lambda x: f"{x} — {df_usuarios[df_usuarios['login'] == x]['nome'].iloc[0]}"
            )
            
            if usuario_sel:
                abas_disponiveis = ["Dashboard", "Despensa", "Famílias", "Agendamentos", "Parceiros", "Voluntários", "Histórico", "Modo SOS", "Mapa Famílias", "Relatórios", "Usuários"]
                permissoes_atuais = carregar_permissoes_abas_neon(usuario_sel)
                
                st.markdown(f"#### Customizando: {usuario_sel}")
                
                # Checkbox para cada aba
                abas_selecionadas = st.multiselect(
                    "Selecione as abas permitidas:",
                    options=abas_disponiveis,
                    default=permissoes_atuais or [],
                    help="Deixe vazio para usar as permissões padrão baseadas no perfil do usuário"
                )
                
                col_save, col_clear = st.columns(2)
                
                with col_save:
                    if st.button("💾 Salvar Permissões", use_container_width=True, type="primary"):
                        if salvar_permissoes_abas_neon(usuario_sel, abas_selecionadas if abas_selecionadas else None):
                            st.success(f"✅ Permissões de {usuario_sel} atualizadas com sucesso!")
                        else:
                            st.error("Erro ao salvar permissões.")
                
                with col_clear:
                    if st.button("🔄 Usar Permissões Padrão", use_container_width=True):
                        if salvar_permissoes_abas_neon(usuario_sel, None):
                            st.success(f"✅ {usuario_sel} voltará a usar as permissões padrão do perfil.")
                        else:
                            st.error("Erro ao limpar permissões.")

    elif menu_opcao == "Voluntários":
        st.markdown("<div class='title-modern'>Gestão de Voluntários</div>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle-modern'>Cadastre e gerencie os voluntários da ação social.</p>", unsafe_allow_html=True)

        with st.expander("➕ Cadastrar Novo Voluntário", expanded=True):
            with st.form("form_voluntario", clear_on_submit=True):
                st.markdown("##### 👤 Dados Pessoais")
                col_v1, col_v2 = st.columns(2)
                nome_vol = col_v1.text_input("Nome Completo *")
                tel_vol = col_v2.text_input("Telefone / WhatsApp *", placeholder="(32) 99999-0000")
                email_vol = st.text_input("E-mail", placeholder="opcional")

                st.markdown("##### 🏠 Endereço")
                col_cep_v, col_num_v = st.columns([1, 2])
                cep_vol = col_cep_v.text_input("CEP *", max_chars=8)
                num_vol = col_num_v.text_input("Número e Complemento *")

                st.markdown("##### 🚗 Transporte")
                possui_veiculo = st.radio("Possui veículo?", ["Não", "Sim"], horizontal=True)
                tipo_veiculo = ""
                if possui_veiculo == "Sim":
                    tipo_veiculo = st.selectbox("Tipo de veículo", ["Carro", "Moto", "Caminhonete/Van", "Caminhão", "Bicicleta"])

                st.markdown("##### 📅 Disponibilidade")
                dias_opcoes = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
                dias_sel = st.multiselect("Dias disponíveis *", dias_opcoes, default=["Sábado"])
                col_h1, col_h2 = st.columns(2)
                hora_inicio = col_h1.time_input("Horário início", value=datetime.time(8, 0))
                hora_fim = col_h2.time_input("Horário fim", value=datetime.time(12, 0))

                obs_vol = st.text_area("Observações", placeholder="Habilidades, restrições, experiência anterior...", height=80)

                if st.form_submit_button("Cadastrar Voluntário", type="primary", use_container_width=True):
                    if nome_vol and tel_vol and cep_vol and num_vol and dias_sel:
                        # Tenta buscar endereço pelo CEP
                        endereco_vol = f"CEP {cep_vol}, {num_vol}"
                        dados_cep_v, ok_cep = buscar_endereco_viacep(cep_vol)
                        if ok_cep:
                            endereco_vol = f"{dados_cep_v.get('logradouro','')}, {num_vol} — {dados_cep_v.get('bairro','')}, {dados_cep_v.get('localidade','')}/{dados_cep_v.get('uf','')}"

                        novo_vol = {
                            'id_voluntario': len(st.session_state.db_voluntarios) + 1,
                            'nome': nome_vol,
                            'telefone': tel_vol,
                            'email': email_vol if email_vol else '-',
                            'cep': cep_vol,
                            'endereco': endereco_vol,
                            'possui_veiculo': possui_veiculo == "Sim",
                            'tipo_veiculo': tipo_veiculo if tipo_veiculo else '-',
                            'dias_disponiveis': ", ".join(dias_sel),
                            'horario_inicio': hora_inicio.strftime('%H:%M'),
                            'horario_fim': hora_fim.strftime('%H:%M'),
                            'observacoes': obs_vol if obs_vol else '-',
                            'data_cadastro': datetime.datetime.now(),
                            'ativo': True
                        }
                        st.session_state.db_voluntarios = pd.concat(
                            [st.session_state.db_voluntarios, pd.DataFrame([novo_vol])],
                            ignore_index=True
                        )
                        salvar_voluntario_neon(novo_vol)
                        st.success(f"✅ Voluntário **{nome_vol}** cadastrado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Preencha os campos obrigatórios: Nome, Telefone, CEP, Número e Dias disponíveis.")

        # --- LISTAGEM DOS VOLUNTÁRIOS ---
        st.markdown("---")
        st.markdown("<div class='title-modern'>Voluntários Cadastrados</div>", unsafe_allow_html=True)

        if not st.session_state.db_voluntarios.empty:
            # Filtro rápido por dia/veículo
            col_filtro1, col_filtro2 = st.columns(2)
            with col_filtro1:
                filtro_dia = st.selectbox(
                    "Filtrar por dia disponível",
                    ["Todos"] + ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
                )
            with col_filtro2:
                filtro_veiculo = st.selectbox("Filtrar por veículo", ["Todos", "Com veículo", "Sem veículo"])

            df_vol_exib = st.session_state.db_voluntarios[st.session_state.db_voluntarios['ativo'] == True].copy()

            if filtro_dia != "Todos":
                df_vol_exib = df_vol_exib[df_vol_exib['dias_disponiveis'].str.contains(filtro_dia, na=False)]

            if filtro_veiculo == "Com veículo":
                df_vol_exib = df_vol_exib[df_vol_exib['possui_veiculo'] == True]
            elif filtro_veiculo == "Sem veículo":
                df_vol_exib = df_vol_exib[df_vol_exib['possui_veiculo'] == False]

            st.markdown(f"<p class='subtitle-modern'>{len(df_vol_exib)} voluntário(s) encontrado(s)</p>", unsafe_allow_html=True)

            for _, vol in df_vol_exib.iterrows():
                with st.container():
                    col_main, col_badge = st.columns([4, 1.2])
                    with col_main:
                        st.markdown(f"### {vol['nome']}")
                        st.write(
                            f"📞 {vol['telefone']}"
                            + (f"  |  ✉️ {vol['email']}" if str(vol.get('email', '-')) != '-' else "")
                        )
                        st.write(f"📍 {vol['endereco']}")
                        st.caption(f"📅 Disponível: {vol['dias_disponiveis']}  |  ⏰ {vol['horario_inicio']} às {vol['horario_fim']}")
                        if str(vol.get('observacoes', '-')) != '-':
                            st.write(f"💬 {vol['observacoes']}")
                    with col_badge:
                        if bool(vol.get('possui_veiculo', False)):
                            st.success(f"🚗 {vol['tipo_veiculo']}")
                        else:
                            st.info("🚶 Sem veículo")

                    st.markdown("---")

                if st.button(f"🗑️ Remover {vol['nome']}", key=f"del_vol_{vol['id_voluntario']}", use_container_width=False):
                    st.session_state.db_voluntarios.loc[
                        st.session_state.db_voluntarios['id_voluntario'] == vol['id_voluntario'], 'ativo'
                    ] = False
                    st.rerun()
        else:
            st.info("Nenhum voluntário cadastrado ainda. Use o formulário acima para adicionar.")

    elif menu_opcao == "Histórico":
        st.markdown("<div class='title-modern'>Registro de Atividades</div>", unsafe_allow_html=True)
        if not st.session_state.db_entregas.empty:
            hist = st.session_state.db_entregas[['id_entrega', 'nome_familia', 'data', 'tipo']].sort_values(by='id_entrega', ascending=False)
            hist.rename(columns={'nome_familia': 'Beneficiado', 'data': 'Data', 'tipo': 'Item'}, inplace=True)
            st.dataframe(hist, use_container_width=True, hide_index=True)
        else:
            st.info("Sem histórico.")

    elif menu_opcao == "Modo SOS":
        st.markdown("""
            <div style="background-color: #FEF2F2; padding: 20px; border-radius: 16px; border: 1px solid #FECACA; margin-bottom: 20px;">
                <h3 style="color: #DC2626; margin: 0;">🚨 Central de Emergência</h3>
                <p style="color: #991B1B; margin-top: 5px;">Gestão de crise e pedidos via WhatsApp.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 📱 Pedidos WhatsApp (Pendente)")
        pedidos_pendentes = st.session_state.db_sos_whatsapp[st.session_state.db_sos_whatsapp['status'] == 'Pendente']
        
        if pedidos_pendentes.empty:
            st.success("✅ Tudo limpo no WhatsApp.")
        else:
            for _, pedido in pedidos_pendentes.iterrows():
                cor_tag = "#DC2626" if pedido['necessidade'] == 'Abrigo' else "#F59E0B"
                hora_formatada = pedido['data_hora'].strftime('%H:%M')
                
                st.markdown(f"""
                    <div class="bento-card" style="border-left: 4px solid {cor_tag};">
                        <div style="display: flex; justify-content: space-between;">
                            <div>
                                <div style="font-weight: 700;">{pedido['nome']}</div>
                                <div class="subtitle-modern">📞 {pedido['telefone']} | 👥 {pedido['pessoas']} pax | 📍 {pedido['cep']}</div>
                                <div style="color: {cor_tag}; font-weight: 600; font-size: 13px;">Necessidade: {pedido['necessidade']}</div>
                            </div>
                            <div style="font-size: 12px; color: #94A3B8;">{hora_formatada}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                c_a, c_b = st.columns(2)
                with c_a:
                    if st.button("✅ Resolver", key=f"res_{pedido['id_msg']}", use_container_width=True):
                        st.session_state.db_sos_whatsapp.loc[st.session_state.db_sos_whatsapp['id_msg'] == pedido['id_msg'], 'status'] = 'Atendido'
                        st.rerun()
                with c_b:
                    if st.button("❌ Dispensar", key=f"disp_{pedido['id_msg']}", use_container_width=True):
                        st.session_state.db_sos_whatsapp.loc[st.session_state.db_sos_whatsapp['id_msg'] == pedido['id_msg'], 'status'] = 'Dispensado'
                        st.rerun()

        st.markdown("---")
        col_checkin, col_rede = st.columns(2)
        
        with col_rede:
            st.markdown("#### Rede de Abrigos")
            cap_total = st.session_state.db_locais_acolhimento['capacidade'].sum()
            ocup_total = st.session_state.db_pessoas_abrigadas['qtd_pessoas'].sum() if not st.session_state.db_pessoas_abrigadas.empty else 0
            st.metric("Vagas Livres", cap_total - ocup_total)

        with col_checkin:
            st.markdown("#### Check-in Vítimas")
            with st.form("form_sos_checkin"):
                opcoes = {loc['id_local']: loc['nome'] for _, loc in st.session_state.db_locais_acolhimento.iterrows()}
                local_sel = st.selectbox("Local", list(opcoes.keys()), format_func=lambda x: opcoes[x])
                nome_sos = st.text_input("Responsável")
                qtd_sos = st.number_input("Qtd Pessoas", min_value=1)
                cep_sos = st.text_input("CEP Origem")
                if st.form_submit_button("Registrar Entrada"):
                    if nome_sos:
                        novo = {'id_acolhido': len(st.session_state.db_pessoas_abrigadas)+1, 'id_local': local_sel, 'nome_responsavel': nome_sos, 'qtd_pessoas': qtd_sos, 'cep_origem': cep_sos, 'endereco_origem': '-', 'lat_origem': None, 'lon_origem': None, 'data_entrada': datetime.datetime.now()}
                        st.session_state.db_pessoas_abrigadas = pd.concat([st.session_state.db_pessoas_abrigadas, pd.DataFrame([novo])], ignore_index=True)
                        
                        # Salva também no Neon
                        salvar_acolhimento_neon(novo)
                        
                        st.success("Acolhido!")
                        st.rerun()

    elif menu_opcao == "Mapa Famílias":
        st.markdown("<div class='title-modern'>Geolocalização (Modo Compatibilidade)</div>", unsafe_allow_html=True)
        st.info("🗺️ Este mapa usa tecnologia leve para garantir a visualização em qualquer dispositivo.")
        
        # 1. Componente de GPS do Usuário
        loc_vol = streamlit_geolocation()
        
        # 2. Prepara dados das Famílias
        df_fam = st.session_state.db_familias.dropna(subset=['lat', 'lon']).copy()
        # Força conversão para números para evitar erros
        df_fam['lat'] = pd.to_numeric(df_fam['lat'], errors='coerce')
        df_fam['lon'] = pd.to_numeric(df_fam['lon'], errors='coerce')
        df_fam['tipo'] = 'familia' # Define que são famílias (Vermelho)
        
        df_sem_mapa = st.session_state.db_familias[st.session_state.db_familias['lat'].isna()]
        
        if not df_sem_mapa.empty:
            st.error(f"⚠️ Atenção: {len(df_sem_mapa)} família(s) não estão aparecendo no mapa por erro de endereço.")
            st.dataframe(df_sem_mapa[['nome', 'endereco', 'cep']], use_container_width=True, hide_index=True)
            st.info("💡 Solução: Exclua o cadastro dessas pessoas e cadastre novamente preenchendo a Latitude e Longitude manualmente.")
            
        # 3. Lógica do GPS do Voluntário
        if loc_vol['latitude'] is not None:
            df_vol = pd.DataFrame([{
                'nome': '📍 VOCÊ (Sua Localização)', 
                'endereco': 'GPS Ativo', 
                'lat': loc_vol['latitude'], 
                'lon': loc_vol['longitude'], 
                'tipo': 'voluntario' # Define que é você (Azul)
            }])
            # Junta tudo
            df_final = pd.concat([df_fam[['nome', 'endereco', 'lat', 'lon', 'tipo']], df_vol])
            
            st.success("✅ GPS Localizado!")
            renderizar_mapa_folium(df_final)
        else:
            # Se não tiver GPS, mostra só as famílias
            st.warning("Clique no ícone de alvo acima para mostrar sua posição.")
            if not df_fam.empty: 
                renderizar_mapa_folium(df_fam)
            else: 
                st.info("Nenhuma família georreferenciada no momento.")
            
    elif menu_opcao == "Relatórios":
        st.markdown("<div class='title-modern'>Central de Relatórios</div>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle-modern'>Selecione o tipo de documento que deseja gerar para impressão ou arquivo.</p>", unsafe_allow_html=True)
        
        col_tipo, col_acao = st.columns([1, 2])
        
        with col_tipo:
            tipo_relatorio = st.radio(
                "Tipo de Documento:",
                ["📋 Estoque Físico (Inventário)", "👥 Famílias na Fila (Espera)", "📦 Histórico de Entregas", "🏠 Ocupação de Abrigos"]
            )
        
        with col_acao:
            st.markdown(f"### Visualização: {tipo_relatorio}")
            
            # --- LÓGICA DO RELATÓRIO DE ESTOQUE ---
            if "Estoque" in tipo_relatorio:
                if not st.session_state.db_lotes.empty:
                    # Junta com o catálogo para pegar o nome
                    df_rep = pd.merge(st.session_state.db_lotes, st.session_state.db_catalogo, on='id_item')
                    # Filtra apenas o que tem quantidade positiva
                    df_rep = df_rep[df_rep['quantidade'] > 0]
                    # Agrupa por produto
                    df_rep = df_rep.groupby('nome').agg({
                        'quantidade': 'sum',
                        'vencimento': 'min' # Pega a data mais próxima de vencer
                    }).reset_index()
                    
                    df_rep.columns = ['Produto / Item', 'Qtd Total', 'Próximo Vencimento']
                    df_rep['Próximo Vencimento'] = pd.to_datetime(df_rep['Próximo Vencimento']).dt.strftime('%d/%m/%Y')
                    
                    titulo_doc = "Inventário de Estoque - Ação Social"
                else:
                    df_rep = pd.DataFrame()
                    st.warning("O estoque está vazio.")

            # --- LÓGICA DO RELATÓRIO DE FAMÍLIAS ---
            elif "Famílias" in tipo_relatorio:
                if not st.session_state.db_familias.empty:
                    df_rep = st.session_state.db_familias[['nome', 'dependentes', 'prioridade', 'endereco', 'igreja']].copy()
                    df_rep.columns = ['Responsável Familiar', 'Dependentes', 'Prioridade', 'Endereço', 'Indicação (Igreja)']
                    titulo_doc = "Lista de Espera para Doação"
                else:
                    df_rep = pd.DataFrame()
                    st.warning("Nenhuma família na fila de espera.")

            # --- LÓGICA DO RELATÓRIO DE HISTÓRICO ---
            elif "Histórico" in tipo_relatorio:
                if not st.session_state.db_entregas.empty:
                    df_rep = st.session_state.db_entregas[['data', 'nome_familia', 'tipo']].copy()
                    df_rep['data'] = pd.to_datetime(df_rep['data']).dt.strftime('%d/%m/%Y')
                    df_rep.columns = ['Data da Entrega', 'Beneficiado', 'Itens Entregues']
                    titulo_doc = "Relatório Geral de Saídas (Entregas)"
                else:
                    df_rep = pd.DataFrame()
                    st.warning("Nenhum histórico de entregas registado.")

            # --- LÓGICA DO RELATÓRIO DE ABRIGOS ---
            elif "Abrigos" in tipo_relatorio:
                if not st.session_state.db_pessoas_abrigadas.empty:
                    df_rep = pd.merge(
                        st.session_state.db_pessoas_abrigadas, 
                        st.session_state.db_locais_acolhimento, 
                        on='id_local'
                    )
                    df_rep = df_rep[['nome_responsavel', 'qtd_pessoas', 'nome', 'data_entrada']]
                    df_rep['data_entrada'] = pd.to_datetime(df_rep['data_entrada']).dt.strftime('%d/%m %H:%M')
                    df_rep.columns = ['Responsável Grupo', 'Qtd Pessoas', 'Local de Acolhimento', 'Chegada']
                    titulo_doc = "Relatório de Ocupação - Abrigos SOS"
                else:
                    df_rep = pd.DataFrame()
                    st.warning("Nenhuma pessoa abrigada no momento.")

            # --- EXIBIÇÃO E BOTÕES DE AÇÃO ---
            if not df_rep.empty:
                # Mostra uma prévia na tela
                st.dataframe(df_rep, use_container_width=True, hide_index=True, height=200)
                
                c_print, c_csv = st.columns(2)
                
                # 1. Botão para Imprimir (Gera HTML em nova aba)
                html_code = gerar_html_impressao(df_rep, titulo_doc, subtitulo=f"Posição em: {datetime.date.today().strftime('%d/%m/%Y')}")
                
                # Codifica o HTML para download/visualização
                import base64
                b64 = base64.b64encode(html_code.encode()).decode()
                href = f'<a href="data:text/html;base64,{b64}" target="_blank" style="text-decoration:none;"><button style="width:100%; padding: 10px; background-color: #4F46E5; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">🖨️ Abrir Visualização de Impressão</button></a>'
                
                with c_print:
                    st.markdown(href, unsafe_allow_html=True)
                    st.caption("Clique para abrir uma página pronta para imprimir (Ctrl+P).")

                # 2. Botão para Excel/CSV
                with c_csv:
                    csv = df_rep.to_csv(index=False).encode('utf-8-sig') # utf-8-sig para acentos funcionarem no Excel
                    st.download_button(
                        label="📥 Baixar Planilha (.csv)",
                        data=csv,
                        file_name=f"relatorio_{datetime.date.today()}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

# ==========================================
# 7. EXECUÇÃO
# ==========================================
if not st.session_state.authenticated:
    login_page()
else:
    main_app()