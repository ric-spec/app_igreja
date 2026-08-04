import importlib.util
import sys
import types
from pathlib import Path

import pandas as pd


class SessionStateProxy(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


class DummyContainer:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def load_app_module(monkeypatch):
    streamlit_stub = types.ModuleType("streamlit")
    streamlit_stub.session_state = SessionStateProxy()
    streamlit_stub.session_state.authenticated = True
    streamlit_stub.session_state.current_user = "admin"
    streamlit_stub.session_state.user_login = "admin"
    streamlit_stub.session_state.user_role = "admin"

    def cache_resource(func=None, *args, **kwargs):
        if func is None:
            return lambda f: f
        return func

    streamlit_stub.cache_resource = cache_resource
    streamlit_stub.cache_data = lambda *args, **kwargs: (lambda func: func)
    streamlit_stub.set_page_config = lambda *args, **kwargs: None
    streamlit_stub.markdown = lambda *args, **kwargs: None
    streamlit_stub.warning = lambda *args, **kwargs: None
    streamlit_stub.success = lambda *args, **kwargs: None
    streamlit_stub.error = lambda *args, **kwargs: None
    streamlit_stub.image = lambda *args, **kwargs: None
    streamlit_stub.columns = lambda *args, **kwargs: [DummyContainer() for _ in range(3)]
    streamlit_stub.button = lambda *args, **kwargs: False
    streamlit_stub.spinner = lambda *args, **kwargs: (lambda f: f)
    streamlit_stub.form = lambda *args, **kwargs: DummyContainer()
    streamlit_stub.form_submit_button = lambda *args, **kwargs: False
    streamlit_stub.sidebar = DummyContainer()
    streamlit_stub.stop = lambda *args, **kwargs: None
    streamlit_stub.text_input = lambda *args, **kwargs: ""
    streamlit_stub.selectbox = lambda *args, **kwargs: None
    streamlit_stub.number_input = lambda *args, **kwargs: 0
    streamlit_stub.radio = lambda *args, **kwargs: None
    streamlit_stub.balloons = lambda *args, **kwargs: None
    streamlit_stub.caption = lambda *args, **kwargs: None
    streamlit_stub.write = lambda *args, **kwargs: None
    streamlit_stub.info = lambda *args, **kwargs: None
    streamlit_stub.metric = lambda *args, **kwargs: None
    streamlit_stub.toast = lambda *args, **kwargs: None
    streamlit_stub.expander = lambda *args, **kwargs: DummyContainer()
    streamlit_stub.download_button = lambda *args, **kwargs: None
    streamlit_stub.secrets = {"postgres": {"url": "sqlite://"}}
    streamlit_stub.pydeck_chart = lambda *args, **kwargs: None

    sys.modules["streamlit"] = streamlit_stub
    sys.modules["pydeck"] = types.ModuleType("pydeck")
    sys.modules["streamlit_geolocation"] = types.ModuleType("streamlit_geolocation")
    sys.modules["streamlit_geolocation"].streamlit_geolocation = lambda *args, **kwargs: None
    sys.modules["folium"] = types.ModuleType("folium")
    sys.modules["streamlit_folium"] = types.ModuleType("streamlit_folium")
    sys.modules["streamlit_folium"].st_folium = lambda *args, **kwargs: None

    spec = importlib.util.spec_from_file_location("app_test", Path(__file__).resolve().parents[1] / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_baixa_avulsa_persiste_estoque(monkeypatch):
    module = load_app_module(monkeypatch)
    module.st.session_state.db_lotes = pd.DataFrame([
        {"id_lote": 1, "id_item": 7, "nome_item": "Açúcar", "quantidade": 5, "vencimento": "2026-09-01"}
    ])

    chamado = []

    def fake_sync():
        chamado.append(True)
        return True

    monkeypatch.setattr(module, "sincronizar_lotes_neon", fake_sync)

    ok, msg = module.dar_baixa_avulsa_peps(7, 3)

    assert ok is True
    assert msg == "Baixa registrada no estoque real."
    assert module.st.session_state.db_lotes.loc[0, "quantidade"] == 2
    assert chamado == [True]


def test_estoque_para_entrega_usa_ordem_alfabetica_e_validade(monkeypatch):
    module = load_app_module(monkeypatch)
    module.st.session_state.db_lotes = pd.DataFrame([
        {"id_lote": 2, "id_item": 2, "nome_item": "Feijão", "quantidade": 3, "vencimento": "2026-10-01"},
        {"id_lote": 1, "id_item": 2, "nome_item": "Feijão", "quantidade": 4, "vencimento": "2026-08-01"},
        {"id_lote": 3, "id_item": 1, "nome_item": "Arroz", "quantidade": 10, "vencimento": "2026-09-15"},
    ])
    module.st.session_state.db_catalogo = pd.DataFrame([
        {"id_item": 1, "nome": "Arroz", "qtd_por_cesta": 0, "categoria": "Avulso"},
        {"id_item": 2, "nome": "Feijão", "qtd_por_cesta": 0, "categoria": "Avulso"},
    ])

    df_estoque = module.obter_df_estoque_para_entrega()

    assert df_estoque["nome"].tolist() == ["Arroz", "Feijão"]
    lotes = module.obter_lotes_disponiveis_por_validade(2)
    assert lotes["id_lote"].tolist() == [1, 2]


def test_baixa_avulsa_nao_depende_da_sincronizacao(monkeypatch):
    module = load_app_module(monkeypatch)
    module.st.session_state.db_lotes = pd.DataFrame([
        {"id_lote": 1, "id_item": 7, "nome_item": "Açúcar", "quantidade": 5, "vencimento": "2026-09-01"}
    ])

    monkeypatch.setattr(module, "sincronizar_lotes_neon", lambda: False)

    ok, msg = module.dar_baixa_avulsa_peps(7, 2)

    assert ok is True
    assert module.st.session_state.db_lotes.loc[0, "quantidade"] == 3
    assert msg == "Baixa registrada no estoque real."
