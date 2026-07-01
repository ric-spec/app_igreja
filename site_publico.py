import os
import streamlit as st
import base64
# Projeto Atos - Site Público
import pandas as pd
import datetime
import hashlib
import logging
import requests
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import locale
import bcrypt

# Configurar locale para português brasileiro
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR')
    except:
        pass

logging.basicConfig(level=logging.INFO)

DEFAULT_CONTACT_PHONE = "(032) 98719-4140"
DEFAULT_CONTACT_EMAIL = "contato@igreja.org"
DEFAULT_CONTACT_WHATSAPP = "(032) 98719-4140"

LOGO_PATH = os.path.join(os.path.dirname(__file__), 'logo_site_igreja.png')

st.set_page_config(
    page_title="Projeto Atos de acolhimento à famílias",
    page_icon=LOGO_PATH,
    layout="wide"
)

def adicionar_fundo_marca_de_agua(caminho_ficheiro):
    """Lê a imagem local, converte para base64 e aplica como fundo com transparência."""
    try:
        with open(caminho_ficheiro, "rb") as f:
            data = f.read()
        bin_str = base64.b64encode(data).decode()
        
        # O linear-gradient aplica uma camada quase opaca (92%) por cima da imagem.
        # Ajustámos a cor para o tom bege (#f7f2eb) que já utiliza no seu projeto.
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(247, 242, 235, 0.92), rgba(247, 242, 235, 0.92)), url("data:image/png;base64,{bin_str}");
            background-size: cover; /* Cobre todo o ecrã */
            background-position: center; /* Mantém a imagem centrada */
            background-attachment: fixed; /* O fundo não se move quando faz scroll */
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Atenção: O ficheiro de imagem '{caminho_ficheiro}' não foi encontrado.")

st.markdown(
    """
    <style>
        .big-title { font-size: 42px; font-weight: 800; margin-bottom: 4px; color: #1e3a22; }
        .subtitle { font-size: 18px; color: #333333; margin-top: 0; margin-bottom: 18px; }
        .card { background: rgba(255, 253, 247, 0.95); border-radius: 18px; padding: 24px; box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15); color: #1a1a1a; }
        .metric-card { border-left: 6px solid #8a5a2b; }
        .help-box { background: rgba(246, 226, 196, 0.95); border-radius: 14px; padding: 22px; margin-top: 16px; border: 1px solid #d9b79d; color: #1a1a1a; }
        .help-box p, .help-box a { color: #1a1a1a; }
        .help-box strong { color: #000000; }
        .item-status { font-weight: 700; }
        .green { color: #14532d; }
        .orange { color: #9a3412; }
        .red { color: #991b1b; }
        a { color: #7b4d29; text-decoration: none; font-weight: 600; }
        a:hover { text-decoration: underline; }
        /* Garantir contraste global */
        p, span, label, div { color: #1a1a1a !important; }
        h1, h2, h3, h4, h5, h6 { color: #1e3a22 !important; }
        
        /* Estilo para botões de Navegação e Formulários */
        div.stButton > button, div.stFormSubmitButton > button {
            background-color: #3e7a49 !important;
            color: white !important;
            border-radius: 10px;
            border: 1px solid #3e7a49;
            transition: all 0.3s ease;
            font-weight: 700;
        }
        
        div.stButton > button:hover, div.stFormSubmitButton > button:hover {
            background-color: #f7f2eb !important;
            color: #1a1a1a !important;
            border: 1px solid #1e3a22;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_resource
def get_engine():
    try:
        conn_url = None
        if hasattr(st, "secrets"):
            postgres = st.secrets.get("postgres", {})
            conn_url = postgres.get("url")

        if not conn_url:
            conn_url = os.environ.get("NEON_URL") or os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")

        if not conn_url:
            raise ValueError("URL de conexão ao Neon não encontrada em st.secrets ou variáveis de ambiente.")

        engine = create_engine(conn_url, pool_pre_ping=True, echo=False)
        if hasattr(st, "session_state"):
            st.session_state.neon_connection_error = None
            st.session_state.neon_connection_url = conn_url
        return engine
    except Exception as e:
        logging.warning(f"Erro ao obter engine Neon: {e}")
        if hasattr(st, "session_state"):
            st.session_state.neon_connection_error = str(e)
            st.session_state.neon_connection_url = None
        return None


def hash_password(password: str) -> str:
    """Gera um hash seguro usando bcrypt com salt automático."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def carregar_usuario_por_login(login):
    engine = get_engine()
    if engine is None:
        return None

    query = "SELECT id_usuario, login, nome, senha_hash, perfil, ativo FROM usuarios WHERE login = %(login)s LIMIT 1;"
    try:
        df = pd.read_sql_query(query, engine, params={"login": login.lower().strip()})
        if df.empty:
            return None
        return df.iloc[0].to_dict()
    except Exception as e:
        logging.warning(f"Erro ao carregar usuário do Neon: {e}")
        return None


def validar_usuario(email, senha):
    login_canonico = email.lower().strip()
    usuario = carregar_usuario_por_login(login_canonico)
    if usuario and usuario.get("ativo", True):
        try:
            if bcrypt.checkpw(senha.encode("utf-8"), usuario["senha_hash"].encode("utf-8")):
                return usuario
        except Exception as e:
            logging.warning(f"Erro ao validar senha com bcrypt: {e}")
    return None


def salvar_usuario_publico(dados_usuario):
    engine = get_engine()
    if engine is None:
        return False

    try:
        dados_usuario = dados_usuario.copy()
        dados_usuario.pop("id_usuario", None)
        senha = dados_usuario.pop("senha", None)
        dados_usuario["senha_hash"] = hash_password(senha or "")
        dados_usuario["login"] = dados_usuario.get("login", "").lower().strip()
        dados_usuario["perfil"] = dados_usuario.get("perfil", "publico")
        df = pd.DataFrame([dados_usuario])
        df.to_sql("usuarios", engine, if_exists="append", index=False)
        return True
    except Exception as e:
        logging.warning(f"Erro ao salvar usuário público no Neon: {e}")
        return False


def buscar_endereco_viacep(cep):
    cep_limpo = "".join(filter(str.isdigit, cep))
    if len(cep_limpo) != 8:
        return None, False
    try:
        url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
        resposta = requests.get(url, timeout=5)
        dados = resposta.json()
        if "erro" not in dados:
            return dados, True
    except Exception:
        pass
    return None, False


def geocodificar_endereco(endereco_busca):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": endereco_busca, "format": "json", "limit": 1}
    headers = {"User-Agent": "IgrejaAcaoSocialApp/1.0"}
    try:
        resposta = requests.get(url, params=params, headers=headers, timeout=5)
        dados = resposta.json()
        if dados:
            return float(dados[0]["lat"]), float(dados[0]["lon"])
    except Exception:
        pass
    return None, None


def carregar_catalogo_neon():
    engine = get_engine()
    if engine is None:
        return pd.DataFrame(columns=["id_item", "nome", "qtd_por_cesta", "categoria"])

    query = "SELECT id_item, nome, qtd_por_cesta, categoria FROM catalogo WHERE ativo = TRUE ORDER BY id_item;"
    try:
        df = pd.read_sql_query(query, engine)
        if "qtd_por_cesta" in df.columns:
            df["qtd_por_cesta"] = df["qtd_por_cesta"].fillna(0).astype(int)
        return df
    except Exception as e:
        logging.warning(f"Erro ao carregar catálogo do Neon: {e}")
        return pd.DataFrame(columns=["id_item", "nome", "qtd_por_cesta", "categoria"])


def carregar_lotes_neon():
    engine = get_engine()
    if engine is None:
        return pd.DataFrame(columns=["id_lote", "id_item", "nome_item", "quantidade", "vencimento"])

    query = "SELECT id_lote, id_item, nome_item, quantidade, vencimento FROM lotes WHERE ativo = TRUE ORDER BY vencimento;"
    try:
        df = pd.read_sql_query(query, engine)
        if "quantidade" in df.columns:
            df["quantidade"] = df["quantidade"].fillna(0).astype(int)
        return df
    except Exception as e:
        logging.warning(f"Erro ao carregar lotes do Neon: {e}")
        return pd.DataFrame(columns=["id_lote", "id_item", "nome_item", "quantidade", "vencimento"])


def salvar_familia_neon(dados_familia):
    engine = get_engine()
    if engine is None:
        return False

    try:
        dados = dados_familia.copy()
        dados.pop("id_familia", None)
        if "data_cadastro" not in dados or not dados["data_cadastro"]:
            dados["data_cadastro"] = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        df = pd.DataFrame([dados])
        df.to_sql("familias", engine, if_exists="append", index=False)
        return True
    except Exception as e:
        logging.warning(f"Erro ao salvar família no Neon: {e}")
        return False


def carregar_contato():
    contato = st.secrets.get("contato", {}) if hasattr(st, "secrets") else {}
    return {
        "telefone": contato.get("telefone", DEFAULT_CONTACT_PHONE),
        "whatsapp": contato.get("whatsapp", DEFAULT_CONTACT_WHATSAPP),
        "email": contato.get("email", DEFAULT_CONTACT_EMAIL),
    }


def formatar_item_para_destaque(item):
    """Formata o nome do item para destaque, limpando espaços e preservando o texto em negrito."""
    texto = str(item or "").strip()
    return f"**{texto}**"


def montar_dashboard(df_catalogo, df_lotes):
    itens = []
    catalogo = df_catalogo.copy()
    lotes = df_lotes.copy()

    if catalogo.empty:
        return pd.DataFrame(columns=["Item", "Qtd por cesta", "Qtd em estoque", "Faltam para 1 cesta"]), pd.DataFrame(columns=["Produto", "Quantidade disponível"]), 0

    catalogo["id_item"] = pd.to_numeric(catalogo["id_item"], errors="coerce")
    catalogo["qtd_por_cesta"] = pd.to_numeric(catalogo["qtd_por_cesta"], errors="coerce").fillna(0).astype(int)
    lotes["id_item"] = pd.to_numeric(lotes["id_item"], errors="coerce")
    lotes["quantidade"] = pd.to_numeric(lotes["quantidade"], errors="coerce").fillna(0).astype(int)

    for _, item in catalogo.iterrows():
        if item["qtd_por_cesta"] <= 0:
            continue

        qtd_estoque = int(lotes[lotes["id_item"] == item["id_item"]]["quantidade"].sum())
        if qtd_estoque == 0 and item.get("nome"):
            qtd_estoque = int(
                lotes[lotes["nome_item"].astype(str).str.strip().str.lower() == str(item["nome"]).strip().lower()]["quantidade"].sum()
            )

        faltam = max(0, int(item["qtd_por_cesta"]) - qtd_estoque)
        itens.append({
            "Item": item["nome"],
            "Qtd por cesta": int(item["qtd_por_cesta"]),
            "Qtd em estoque": qtd_estoque,
            "Faltam para 1 cesta": int(faltam),
        })

    df_criticos = pd.DataFrame(itens, columns=["Item", "Qtd por cesta", "Qtd em estoque", "Faltam para 1 cesta"])
    if not df_criticos.empty:
        df_criticos = df_criticos.sort_values(by=["Faltam para 1 cesta", "Qtd em estoque"], ascending=[False, True])

    estoque_geral = lotes.groupby(["id_item", "nome_item"], as_index=False)["quantidade"].sum()
    estoque_geral = estoque_geral.sort_values(by="quantidade", ascending=False)
    estoque_geral.rename(columns={"nome_item": "Produto", "quantidade": "Quantidade disponível"}, inplace=True)

    return df_criticos, estoque_geral, 0


def main():
    adicionar_fundo_marca_de_agua(LOGO_PATH)
    
    # Inserir Logo no topo
    col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 1, 1])
    with col_logo_2:
        try:
            st.image(LOGO_PATH, width=200)
        except:
            pass

    contato = carregar_contato()

    if 'neon_connection_error' not in st.session_state:
        st.session_state.neon_connection_error = None
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Sobre o projeto"

    df_catalogo = carregar_catalogo_neon()
    df_lotes = carregar_lotes_neon()
    df_falta, df_estoque, cestas_possiveis = montar_dashboard(df_catalogo, df_lotes)

    total_itens_catalogo = len(df_catalogo)
    total_itens_criticos = 0 if df_falta.empty else df_falta['Faltam para 1 cesta'].gt(0).sum()

    # Título
    st.markdown("<div class='big-title'>PROJETO ATOS - PIBJF Cascatinha</div>", unsafe_allow_html=True)
    
    # Navegação horizontal com botões
    col_nav = st.columns(3)
    pages = ["Sobre o projeto", "Quero Contribuir", "Preciso de ajuda"]
    
    for idx, page in enumerate(pages):
        with col_nav[idx]:
            if st.button(page, use_container_width=True, key=f"nav_{page}"):
                st.session_state.current_page = page
    
    st.markdown("---")

    if st.session_state.neon_connection_error:
        st.error(f"❌ Erro ao conectar ao Neon: {st.session_state.neon_connection_error}")
        st.warning("Verifique se a URL está em st.secrets['postgres']['url'] ou na variável de ambiente NEON_URL / DATABASE_URL / POSTGRES_URL.")
        if st.session_state.get('neon_connection_url'):
            st.info(f"Host de conexão usado: {st.session_state.neon_connection_url.split('@')[1].split('/')[0]}")


    # Conteúdo Sobre o projeto (página principal)
    if st.session_state.current_page == "Sobre o projeto":
        st.markdown("<div class='subtitle'>Página de apoio para famílias que precisam de cesta básica e informação direta.</div>", unsafe_allow_html=True)
        
        st.markdown(
            """
            ## Ministério Atos

            ### Inspirado em Atos 4. Conectado pelo Amor. Movido pelo Serviço.
            O Ministério Atos é uma iniciativa social da PIBJF Cascatinha dedicada a levar cuidado, dignidade e esperança às pessoas por meio da arrecadação e distribuição de itens essenciais.

            Inspirados pelo exemplo da igreja primitiva descrito em Atos 4, acreditamos que a fé deve se manifestar em ações concretas de amor ao próximo. Assim como os primeiros cristãos compartilhavam seus recursos para que ninguém passasse necessidade, buscamos ser instrumentos de provisão, solidariedade e transformação em nossa comunidade.

            ### Nossa Missão
            Promover ações sociais que atendam necessidades básicas de famílias e indivíduos, demonstrando o amor de Cristo através do cuidado prático e do serviço ao próximo.

            ### Nossa Visão
            Ser uma ponte entre aqueles que podem ajudar e aqueles que necessitam de apoio, fortalecendo a comunidade por meio da generosidade, da compaixão e da unidade.

            ### O Que Fazemos

            - Arrecadação e distribuição de cestas básicas.
            - Doação de roupas, calçados e cobertores.
            - Entrega de materiais de higiene pessoal.
            - Apoio emergencial a famílias em situação de vulnerabilidade.
            - Mobilização de voluntários para ações comunitárias.
            - Desenvolvimento de campanhas solidárias ao longo do ano.

            ### Nossa Base Bíblica
            "Não havia entre eles necessitado algum." — Atos 4:34

            Este versículo expressa a essência do Ministério Atos: unir pessoas, recursos e propósito para que o amor de Deus seja demonstrado de forma prática, alcançando aqueles que mais precisam.
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class='help-box'>
                <p><strong>Contato rápido:</strong></p>
                <p>Telefone: <a href='tel:{contato['telefone']}'>{contato['telefone']}</a></p>
                <p>WhatsApp: <a href='https://wa.me/{contato['whatsapp'].replace('(', '').replace(')', '').replace(' ', '').replace('-', '')}' target='_blank'>{contato['whatsapp']}</a></p>
                <p>E-mail: <a href='mailto:{contato['email']}'>{contato['email']}</a></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Aba Quero Contribuir
    elif st.session_state.current_page == "Quero Contribuir":
        st.markdown("<div class='subtitle'>Itens que faltam para montar 1 cesta básica completa para uma família com 4 pessoas.</div>", unsafe_allow_html=True)
        st.markdown("<h3>O que precisamos</h3>", unsafe_allow_html=True)
        st.markdown(f"<p><strong>{total_itens_criticos}</strong> item(ns) ainda faltam para completar 1 cesta básica.</p>", unsafe_allow_html=True)
        
        if df_falta.empty:
            st.success("✅ Estoque completo para montar 1 cesta básica.")
        else:
            df_falta_sorted = df_falta[df_falta['Faltam para 1 cesta'] > 0].sort_values(by='Faltam para 1 cesta', ascending=False)
            st.markdown("#### Itens que ainda faltam:")
            for _, row in df_falta_sorted.iterrows():
                st.markdown(f"- {formatar_item_para_destaque(row['Item'])} — faltam {row['Faltam para 1 cesta']} unidade(s) para 1 cesta")

    # Aba Preciso de ajuda
    elif st.session_state.current_page == "Preciso de ajuda":
        st.markdown("<div class='subtitle'>Acesso para famílias cadastrar solicitações de ajuda.</div>", unsafe_allow_html=True)
        st.markdown("<h3>Cadastro de família</h3>", unsafe_allow_html=True)

        if 'public_authenticated' not in st.session_state:
            st.session_state.public_authenticated = False
            st.session_state.public_user_login = None
        if 'public_request_type' not in st.session_state:
            st.session_state.public_request_type = None

        if not st.session_state.public_authenticated:
            st.markdown("<p>Para acessar o cadastro de família e solicitar itens, faça login ou cadastre-se.</p>", unsafe_allow_html=True)
            acesso_opcao = st.radio("Escolha uma opção:", ["Entrar", "Cadastrar"], horizontal=True)

            if acesso_opcao == "Entrar":
                with st.form("form_login_familia"):
                    email = st.text_input("E-mail de acesso (*)", placeholder="seu@email.com")
                    senha = st.text_input("Senha (*)", type="password")
                    login_submit = st.form_submit_button("Entrar")
                    if login_submit:
                        with st.spinner("Validando credenciais..."):
                            if not email.strip() or not senha.strip():
                                st.error("Informe e-mail e senha para continuar.")
                            else:
                                usuario_info = validar_usuario(email, senha)
                                if usuario_info:
                                    st.session_state.public_authenticated = True
                                    st.session_state.public_user_login = usuario_info["login"]
                                    st.success("Login realizado com sucesso.")
                                    st.rerun()
                                else:
                                    st.error("Credenciais inválidas. Verifique e tente novamente.")

            else:
                with st.form("form_cadastrar_publico"):
                    nome_cadastro = st.text_input("Nome completo (*)")
                    email_cadastro = st.text_input("E-mail de acesso (*)", placeholder="seu@email.com")
                    senha_cadastro = st.text_input("Senha (*)", type="password")
                    senha_confirm = st.text_input("Confirme a senha (*)", type="password")
                    pedido_opcao = st.selectbox("O que você deseja solicitar?", ["Cesta Básica", "Itens do estoque"])
                    cadastrar_submit = st.form_submit_button("Cadastrar e continuar")

                    if cadastrar_submit:
                        with st.spinner("Criando sua conta..."):
                            if not nome_cadastro.strip() or not email_cadastro.strip() or not senha_cadastro.strip() or not senha_confirm.strip():
                                st.error("Preencha todos os campos obrigatórios para cadastrar.")
                            elif senha_cadastro != senha_confirm:
                                st.error("As senhas não conferem.")
                            else:
                                usuario_novo = {
                                    "login": email_cadastro.lower().strip(),
                                    "nome": nome_cadastro.strip(),
                                    "senha": senha_cadastro,
                                    "perfil": "publico",
                                    "ativo": True,
                                }
                                if salvar_usuario_publico(usuario_novo):
                                    st.session_state.public_authenticated = True
                                    st.session_state.public_user_login = usuario_novo["login"]
                                    st.session_state.public_request_type = pedido_opcao
                                    st.success("Cadastro realizado com sucesso. Você já pode continuar com o pedido.")
                                    st.rerun()
                                else:
                                    st.error("Não foi possível cadastrar. Verifique se o e-mail já está em uso.")
        else:
            st.markdown(f"<div style='margin-bottom: 16px; color: #166534;'>Acesso liberado para <strong>{st.session_state.public_user_login}</strong>. <a href='#' id='logout-link'>Sair</a></div>", unsafe_allow_html=True)
            if st.button("Sair do cadastro", key="logout_button"):
                st.session_state.public_authenticated = False
                st.session_state.public_user_login = None
                st.rerun()

            with st.form("form_cadastro_familia"):
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

                st.markdown("##### Pedido")
                pedido_tipo_options = ["Cesta Básica", "Itens do estoque"]
                pedido_index = pedido_tipo_options.index(st.session_state.public_request_type) if st.session_state.public_request_type in pedido_tipo_options else 0
                pedido_tipo = st.selectbox("Selecione o que deseja solicitar", pedido_tipo_options, index=pedido_index)

                st.markdown("##### 📍 Coordenadas (Opcional - use se o mapa automático falhar)")
                st.caption("Dica: No Google Maps, clique com o botão direito no local e copie os números em formato -23.5500, -46.6330")
                c_lat, c_lon = st.columns(2)
                lat_manual = c_lat.text_input("Latitude")
                lon_manual = c_lon.text_input("Longitude")

                st.markdown("##### Dados Eclesiásticos")
                col_igreja, col_pastor = st.columns(2)
                igreja = col_igreja.text_input("Nome da Igreja")
                pastor = col_pastor.text_input("Nome do Pastor")

                if st.form_submit_button("Cadastrar Família", type="primary"):
                    with st.spinner("Processando cadastro da família..."):
                        if not nome or not telefone or not cep or not numero:
                            st.error("Preencha todos os campos obrigatórios marcados com *.")
                        else:
                            lat, lon = None, None
                        endereco_display = "Endereço em processamento"

                        if lat_manual and lon_manual:
                            try:
                                lat = float(lat_manual.replace(',', '.'))
                                lon = float(lon_manual.replace(',', '.'))
                            except ValueError:
                                st.warning("Coordenadas manuais inválidas. Tentando busca automática...")

                        if lat is None:
                            dados_cep, sucesso_cep = buscar_endereco_viacep(cep)
                            if sucesso_cep:
                                endereco_display = f"{dados_cep.get('logradouro','')}, {numero} - {dados_cep.get('bairro','')}"
                                lat, lon = geocodificar_endereco(f"{endereco_display}, {dados_cep.get('localidade','')}, Brasil")
                            else:
                                endereco_display = f"CEP {cep}, {numero}"

                        dados_familia = {
                            "nome": nome,
                            "dependentes": dep,
                            "prioridade": prio.split()[0],
                            "telefone": telefone,
                            "atendimento_tipo": pedido_tipo,
                            "cep": cep,
                            "endereco": endereco_display,
                            "lat": lat,
                            "lon": lon,
                            "igreja": igreja if igreja else "Não informado",
                            "pastor": pastor if pastor else "-",
                            "ultima_entrega": None,
                            "data_cadastro": datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                            "ativo": True,
                        }

                        if salvar_familia_neon(dados_familia):
                            if lat is not None:
                                st.success("✅ Cadastro realizado e localizado com sucesso.")
                            else:
                                st.warning("Cadastro realizado, mas o endereço não pôde ser geolocalizado automaticamente.")
                            st.balloons()
                        else:
                            st.error("Não foi possível registrar a família. Tente novamente mais tarde.")
        
        st.markdown("<div class='help-box'>Caso tenha dificuldade para preencher o formulário, mande uma mensagem pelo WhatsApp (032) 98719-4140 ou ligue para o número (032) 98719-4140.</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
