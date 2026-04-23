import streamlit as st
import pandas as pd
import datetime
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
        engine = create_engine(conn_url, echo=False)
        return engine
    except Exception as e:
        st.error(f"❌ Erro ao conectar ao Neon: {e}")
        return None

def salvar_familia_neon(dados_familia):
    """Salva dados de uma família no Neon"""
    try:
        engine = get_engine()
        if engine is None:
            return False
        
        df = pd.DataFrame([dados_familia])
        df.to_sql('familias', engine, if_exists='append', index=False)
        st.success("✅ Família salva no Neon com sucesso!")
        return True
    except Exception as e:
        st.warning(f"⚠️ Erro ao salvar família no Neon: {e}")
        return False

def salvar_entrega_neon(dados_entrega):
    """Salva dados de uma entrega no Neon"""
    try:
        engine = get_engine()
        if engine is None:
            return False
        
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

def salvar_item_catalogo_neon(dados_item):
    """Salva um novo item no catálogo de despensa do Neon"""
    try:
        engine = get_engine()
        if engine is None:
            return False
        
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
        
        df = pd.DataFrame([dados_lote])
        df.to_sql('lotes', engine, if_exists='append', index=False)
        st.success("✅ Lote de estoque registrado com sucesso!")
        return True
    except Exception as e:
        st.warning(f"⚠️ Erro ao salvar lote: {e}")
        return False

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

        with engine.connect() as conn:
            # Script completo de migração
            schema_sql = """
                CREATE TABLE IF NOT EXISTS familias (id_familia SERIAL PRIMARY KEY, nome VARCHAR(255) NOT NULL, dependentes INTEGER, prioridade VARCHAR(50), cep VARCHAR(10), endereco TEXT, lat FLOAT, lon FLOAT, igreja VARCHAR(255), pastor VARCHAR(255), ultima_entrega TIMESTAMP, data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP, ativo BOOLEAN DEFAULT TRUE);
                CREATE TABLE IF NOT EXISTS entregas (id_entrega SERIAL PRIMARY KEY, id_familia INTEGER, nome_familia VARCHAR(255), data TIMESTAMP, tipo VARCHAR(255), itens TEXT, responsavel_entrega VARCHAR(255), data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (id_familia) REFERENCES familias(id_familia));
                CREATE TABLE IF NOT EXISTS sos_whatsapp (id_msg SERIAL PRIMARY KEY, telefone VARCHAR(20), nome VARCHAR(255), necessidade VARCHAR(255), pessoas INTEGER, cep VARCHAR(10), endereco TEXT, status VARCHAR(50), data_hora TIMESTAMP, respondido_por VARCHAR(255), data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS locais_acolhimento (id_local SERIAL PRIMARY KEY, nome VARCHAR(255), tipo VARCHAR(100), capacidade INTEGER, cep VARCHAR(10), endereco TEXT, lat FLOAT, lon FLOAT, ativo BOOLEAN DEFAULT TRUE, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS pessoas_abrigadas (id_acolhido SERIAL PRIMARY KEY, id_local INTEGER, nome_responsavel VARCHAR(255), qtd_pessoas INTEGER, cep_origem VARCHAR(10), endereco_origem TEXT, lat_origem FLOAT, lon_origem FLOAT, data_entrada TIMESTAMP, responsavel_checkin VARCHAR(255), data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (id_local) REFERENCES locais_acolhimento(id_local));
                CREATE TABLE IF NOT EXISTS atendimentos (id_atendimento SERIAL PRIMARY KEY, pessoa_nome VARCHAR(255), tipo_atendimento VARCHAR(255), descricao TEXT, data_atendimento TIMESTAMP, status VARCHAR(50), responsavel VARCHAR(255), data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS catalogo (id_item SERIAL PRIMARY KEY, nome VARCHAR(255) NOT NULL, qtd_por_cesta INTEGER DEFAULT 1, categoria VARCHAR(100), ativo BOOLEAN DEFAULT TRUE, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS lotes (id_lote SERIAL PRIMARY KEY, id_item INTEGER, nome_item VARCHAR(255), quantidade INTEGER, vencimento DATE, local_armazenagem VARCHAR(255), data_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP, ativo BOOLEAN DEFAULT TRUE, FOREIGN KEY (id_item) REFERENCES catalogo(id_item));
                CREATE INDEX IF NOT EXISTS idx_familias_nome ON familias(nome);
                CREATE INDEX IF NOT EXISTS idx_sos_status ON sos_whatsapp(status);
            """
            from sqlalchemy import text
            conn.execute(text(schema_sql))
            conn.commit()
            
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
        --primary: #2563eb;
        --primary-light: #3b82f6;
        --primary-dark: #1d4ed8;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --bg-app: #f0f4f8;
        --bg-card: #ffffff;
        --text-main: #1f2937;
        --text-light: #6b7280;
        --border: #e5e7eb;
        --shadow: 0 2px 8px rgba(0,0,0,0.1);
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
    .badge-success { background: #d1fae5; color: #065f46; }
    .badge-warning { background: #fef3c7; color: #78350f; }
    .badge-danger { background: #fee2e2; color: #7f1d1d; }
    .badge-info { background: #dbeafe; color: #0c2340; }

    /* BOTÕES - Maiores e Mais Visíveis */
    .stButton > button {
        font-size: 16px !important;
        padding: 12px 24px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.2s !important;
        height: auto !important;
        min-height: 44px !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* TEXTOS DE ENTRADA - Maiores */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        font-size: 15px !important;
        padding: 12px !important;
        border-radius: 8px !important;
        min-height: 40px !important;
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
        background: #f3f4f6;
        border-left-color: var(--primary);
    }
    .menu-item.active {
        background: var(--primary);
        color: white;
        border: 1px solid var(--primary);
    }

    /* LOGIN - Mais Acessível */
    .login-box {
        background: white;
        padding: 40px;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        max-width: 420px;
        margin: auto;
    }
    .login-box h1 {
        font-size: 28px;
        margin-bottom: 8px;
        color: var(--primary);
    }
    .login-box p {
        color: var(--text-light);
        margin-bottom: 24px;
        font-size: 15px;
    }

    /* TABELAS - Legíveis */
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th {
        background: var(--primary);
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: 600;
    }
    td {
        padding: 12px;
        border-bottom: 1px solid var(--border);
    }
    tr:hover { background: #f9fafb; }

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
        background-color: var(--bg-app);
        border-right: 1px solid var(--border);
        padding: 20px 16px;
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

def login_page():
    # Centraliza o conteúdo vertical e horizontalmente usando colunas
    st.markdown("", unsafe_allow_html=True) 
    col1, col2, col3 = st.columns([1, 1, 1]) # Ajuste para telas grandes
    
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="login-box">
            <h1 style='color: #4F46E5; margin-bottom: 0;'>Atos 4</h1>
            <p style='color: #64748B; font-size: 14px; margin-bottom: 30px;'>Acesse o sistema</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            usuario = st.text_input("Usuário", placeholder="admin")
            senha = st.text_input("Senha", type="password", placeholder="••••••")
            submit = st.form_submit_button("Entrar no Sistema", use_container_width=True, type="primary")
            
            if submit:
                # Simulação de autenticação (Hardcoded para demo)
                if usuario == "admin" and senha == "pibjf":
                    st.session_state.authenticated = True
                    st.toast("Login realizado com sucesso!", icon="🎉")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Credenciais inválidas. Tente novamente.")
        
        st.markdown("""
            <div style='text-align: center; margin-top: 20px; color: #94A3B8; font-size: 12px;'>
                Esqueceu a senha? Contate o administrador da igreja.
            </div>
        """, unsafe_allow_html=True)

def logout():
    st.session_state.authenticated = False
    st.rerun()

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
        {'id_item': 1, 'nome': 'Arroz (5kg)', 'qtd_por_cesta': 1},
        {'id_item': 2, 'nome': 'Feijão (1kg)', 'qtd_por_cesta': 2},
        {'id_item': 3, 'nome': 'Macarrão (500g)', 'qtd_por_cesta': 2},
        {'id_item': 4, 'nome': 'Farinha de Trigo (1kg)', 'qtd_por_cesta': 1},
        
        # Óleos e Condimentos
        {'id_item': 5, 'nome': 'Óleo de Soja (900ml)', 'qtd_por_cesta': 1},
        {'id_item': 6, 'nome': 'Sal (1kg)', 'qtd_por_cesta': 1},
        {'id_item': 7, 'nome': 'Açúcar (1kg)', 'qtd_por_cesta': 1},
        
        # Laticínios e Proteínas
        {'id_item': 8, 'nome': 'Leite em Pó (400g)', 'qtd_por_cesta': 1},
        {'id_item': 9, 'nome': 'Ovo (dúzia)', 'qtd_por_cesta': 1},
        {'id_item': 10, 'nome': 'Sardinha em Lata (120g)', 'qtd_por_cesta': 1},
        
        # Frutas e Vegetais
        {'id_item': 11, 'nome': 'Batata-doce (kg)', 'qtd_por_cesta': 1},
        {'id_item': 12, 'nome': 'Cebola (kg)', 'qtd_por_cesta': 1},
        
        # Bebidas
        {'id_item': 13, 'nome': 'Café (500g)', 'qtd_por_cesta': 1},
        {'id_item': 14, 'nome': 'Achocolatado (400g)', 'qtd_por_cesta': 1},
        
        # Produtos de Higiene/Limpeza
        {'id_item': 15, 'nome': 'Sabão em Pó (500g)', 'qtd_por_cesta': 1},
        {'id_item': 16, 'nome': 'Desinfetante (1L)', 'qtd_por_cesta': 1},
        {'id_item': 17, 'nome': 'Sabonete (unidade)', 'qtd_por_cesta': 1},
    ])

if 'db_lotes' not in st.session_state:
    st.session_state.db_lotes = pd.DataFrame([
        # Grãos - Arroz
        {'id_lote': 1, 'id_item': 1, 'quantidade': 25, 'vencimento': datetime.date(2026, 12, 1)},
        
        # Grãos - Feijão
        {'id_lote': 2, 'id_item': 2, 'quantidade': 30, 'vencimento': datetime.date(2026, 8, 15)},
        {'id_lote': 3, 'id_item': 2, 'quantidade': 15, 'vencimento': datetime.date(2026, 9, 20)},
        
        # Macarrão
        {'id_lote': 4, 'id_item': 3, 'quantidade': 40, 'vencimento': datetime.date(2026, 11, 15)},
        
        # Farinha
        {'id_lote': 5, 'id_item': 4, 'quantidade': 20, 'vencimento': datetime.date(2026, 10, 10)},
        
        # Óleo
        {'id_lote': 6, 'id_item': 5, 'quantidade': 35, 'vencimento': datetime.date(2026, 3, 20)},
        
        # Sal
        {'id_lote': 7, 'id_item': 6, 'quantidade': 50, 'vencimento': datetime.date(2027, 6, 15)},
        
        # Açúcar
        {'id_lote': 8, 'id_item': 7, 'quantidade': 30, 'vencimento': datetime.date(2026, 7, 30)},
        
        # Leite em Pó
        {'id_lote': 9, 'id_item': 8, 'quantidade': 18, 'vencimento': datetime.date(2026, 5, 15)},
        
        # Ovos
        {'id_lote': 10, 'id_item': 9, 'quantidade': 12, 'vencimento': datetime.date(2026, 4, 30)},
        
        # Sardinha
        {'id_lote': 11, 'id_item': 10, 'quantidade': 25, 'vencimento': datetime.date(2026, 9, 10)},
        
        # Batata-doce
        {'id_lote': 12, 'id_item': 11, 'quantidade': 40, 'vencimento': datetime.date(2026, 5, 20)},
        
        # Cebola
        {'id_lote': 13, 'id_item': 12, 'quantidade': 35, 'vencimento': datetime.date(2026, 6, 10)},
        
        # Café
        {'id_lote': 14, 'id_item': 13, 'quantidade': 20, 'vencimento': datetime.date(2026, 12, 15)},
        
        # Achocolatado
        {'id_lote': 15, 'id_item': 14, 'quantidade': 15, 'vencimento': datetime.date(2026, 8, 20)},
        
        # Sabão em Pó
        {'id_lote': 16, 'id_item': 15, 'quantidade': 22, 'vencimento': datetime.date(2026, 10, 25)},
        
        # Desinfetante
        {'id_lote': 17, 'id_item': 16, 'quantidade': 18, 'vencimento': datetime.date(2026, 9, 5)},
        
        # Sabonete
        {'id_lote': 18, 'id_item': 17, 'quantidade': 48, 'vencimento': datetime.date(2026, 11, 30)},
    ])

if 'db_familias' not in st.session_state:
    st.session_state.db_familias = pd.DataFrame([
        {
            'id_familia': 1, 'nome': 'Maria de Fátima', 'dependentes': 3, 'prioridade': 'Alta', 
            'cep': '36010001', 'endereco': 'Av. Barão do Rio Branco, 100 - Centro, Juiz de Fora/MG', 
            'lat': -21.7611, 'lon': -43.3444, 
            'igreja': 'Igreja Batista Central', 'pastor': 'Pr. Carlos',
            'ultima_entrega': None
        }
    ])

if 'db_entregas' not in st.session_state:
    st.session_state.db_entregas = pd.DataFrame(columns=['id_entrega', 'nome_familia', 'data', 'tipo'])

if 'db_locais_acolhimento' not in st.session_state:
    st.session_state.db_locais_acolhimento = pd.DataFrame([
        {'id_local': 1, 'nome': 'Salão Principal da Igreja', 'tipo': 'Igreja', 'capacidade': 30, 'cep': '36010001', 'endereco': 'Sede', 'lat': -21.7600, 'lon': -43.3400}
    ])

if 'db_pessoas_abrigadas' not in st.session_state:
    st.session_state.db_pessoas_abrigadas = pd.DataFrame(columns=['id_acolhido', 'id_local', 'nome_responsavel', 'qtd_pessoas', 'cep_origem', 'endereco_origem', 'lat_origem', 'lon_origem', 'data_entrada'])

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
            
    nova_entrega = {'id_entrega': len(st.session_state.db_entregas)+1, 'nome_familia': nome_familia, 'data': datetime.date.today(), 'tipo': 'Cesta Padrão'}
    st.session_state.db_entregas = pd.concat([st.session_state.db_entregas, pd.DataFrame([nova_entrega])], ignore_index=True)
    
    # Salva também no Neon
    salvar_entrega_neon(nova_entrega)
    
    excluir_familia_manual(id_familia)
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

def renderizar_mapa_alto_contraste(df_mapa, zoom_level=12, estilo_selecionado="Claro"):
    """
    Gera um mapa interativo com opções de visualização melhoradas.
    """
    df_mapa = df_mapa.dropna(subset=['lat', 'lon']).copy()
    if df_mapa.empty: return
    
    # Define o estilo do mapa com base na escolha
    map_styles = {
        "Claro": "carto-positron",       # Fundo branco (Melhor contraste)
        "Escuro": "carto-dark-matter",   # Fundo preto
        "Estradas": "road"               # Mapa de ruas padrão
    }
    style_uri = map_styles.get(estilo_selecionado, "carto-positron")

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
            "html": "<div style='color:white; background:#1e293b; padding:10px; border-radius:5px;'><b>{nome}</b><br>{endereco}</div>"
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
        body { font-family: 'Roboto', sans-serif; color: #000; padding: 20px; background: #fff; }
        h1 { text-align: center; text-transform: uppercase; font-size: 18px; margin-bottom: 5px; color: #222; }
        h2 { text-align: center; font-size: 14px; font-weight: normal; margin-bottom: 30px; color: #555; }
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
    # --- Sidebar de Navegação ---
    with st.sidebar:
        st.markdown(f"### Olá, Admin 👋")
        st.markdown("---")
        menu_opcao = st.radio(
            "Navegação",
            ["Dashboard", "Despensa", "Famílias", "Histórico", "Modo SOS", "Mapa Famílias", "Relatórios"],
            label_visibility="collapsed"
        )
        
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
        col_entrada, col_catalogo = st.columns([2, 1])
        
        with col_catalogo:
            st.markdown("<div class='title-modern'>Novo Tipo de Item</div>", unsafe_allow_html=True)
            with st.form("form_novo_catalogo", clear_on_submit=True):
                novo_nome = st.text_input("Nome")
                tipo_item = st.radio("Regra:", ["Item Avulso/Extra", "Obrigatório na Cesta"])
                qtd_cesta = st.number_input("Qtd por Cesta", min_value=1, value=1) if "Obrigatório" in tipo_item else 0
                
                if st.form_submit_button("Adicionar", type="primary", use_container_width=True):
                    if novo_nome:
                        novo_id = st.session_state.db_catalogo['id_item'].max() + 1 if not st.session_state.db_catalogo.empty else 1
                        novo_item = {'id_item': novo_id, 'nome': novo_nome, 'qtd_por_cesta': qtd_cesta}
                        st.session_state.db_catalogo = pd.concat([st.session_state.db_catalogo, pd.DataFrame([novo_item])], ignore_index=True)
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
                    novo_lote = {'id_lote': len(st.session_state.db_lotes)+1, 'id_item': id_item_escolhido, 'quantidade': qtd, 'vencimento': venc}
                    st.session_state.db_lotes = pd.concat([st.session_state.db_lotes, pd.DataFrame([novo_lote])], ignore_index=True)
                    st.success("Registado!")
                    st.rerun()

        st.markdown("---")
        st.markdown("<div class='title-modern'>Estoque Físico Atual</div>", unsafe_allow_html=True)
        if not st.session_state.db_lotes.empty and st.session_state.db_lotes['quantidade'].sum() > 0:
            df_exibicao = pd.merge(st.session_state.db_lotes[st.session_state.db_lotes['quantidade'] > 0], st.session_state.db_catalogo, on='id_item')
            df_exibicao = df_exibicao[['nome', 'quantidade', 'vencimento']].sort_values(by='vencimento')
            df_exibicao['vencimento'] = pd.to_datetime(df_exibicao['vencimento']).dt.strftime('%d/%m/%Y')
            df_exibicao.rename(columns={'nome': 'Produto', 'quantidade': 'Qtd Disponível', 'vencimento': 'Vence em'}, inplace=True)
            st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
        else:
            st.info("A despensa está vazia.")

    elif menu_opcao == "Famílias":
        c1, c2 = st.columns([3, 1])
        c1.markdown("<div class='title-modern'>Fila de Espera</div>", unsafe_allow_html=True)
        
        with st.expander("➕ Cadastrar Nova Família", expanded=True):
            with st.form("form_familia", clear_on_submit=True):
                st.markdown("##### Dados Pessoais")
                nome = st.text_input("Nome do Responsável *")
                col_dep, col_prio = st.columns(2)
                dep = col_dep.number_input("Número de Dependentes", min_value=0)
                prio = col_prio.selectbox("Prioridade", ["Normal", "Alta (Urgência)"])
                
                st.markdown("##### Endereço e Localização")
                col_cep, col_num = st.columns([1, 2])
                cep = col_cep.text_input("CEP (Somente números) *", max_chars=8)
                numero = col_num.text_input("Número e Complemento *")
                
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
                    if nome and cep and numero:
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
                            'nome': nome, 'dependentes': dep, 'prioridade': prio.split(" ")[0],
                            'cep': cep, 'endereco': endereco_display,
                            'lat': lat, 'lon': lon, # Pode ser None se falhar
                            'igreja': igreja if igreja else 'Não informado', 'pastor': pastor if pastor else '-',
                            'ultima_entrega': None
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
                
                st.markdown(f"""
                    <div class="bento-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <div class="title-modern" style="font-size: 18px;">{fam['nome']}</div>
                                <div class="subtitle-modern">
                                    👥 {fam['dependentes']} Dep. | {fam['endereco']}
                                </div>
                                <div style="font-size: 12px; margin-top: 5px; color: #64748B;">{status_mapa}</div>
                            </div>
                            {tag_prio}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button(f"📦 Entregar", key=f"ent_{fam['id_familia']}", use_container_width=True):
                        suc, msg = alocar_cesta_peps(fam['id_familia'])
                        if suc: st.success(msg); st.rerun()
                        else: st.error(msg)
                with c_btn2:
                    if st.button(f"🗑️ Excluir", key=f"exc_{fam['id_familia']}", use_container_width=True):
                        excluir_familia_manual(fam['id_familia'])
                        st.rerun()
        else:
            st.info("Nenhuma família cadastrada.")

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
