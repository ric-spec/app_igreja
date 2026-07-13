import importlib.util
import sys
import types
from pathlib import Path

import pandas as pd


class DummyContainer:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class SessionStateProxy(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


def load_app_module():
    streamlit_stub = types.ModuleType("streamlit")
    streamlit_stub.session_state = SessionStateProxy()
    streamlit_stub.cache_resource = lambda func: func
    streamlit_stub.secrets = {"postgres": {"url": "sqlite://"}}
    streamlit_stub.error = lambda *args, **kwargs: None
    streamlit_stub.warning = lambda *args, **kwargs: None
    streamlit_stub.success = lambda *args, **kwargs: None
    streamlit_stub.info = lambda *args, **kwargs: None
    streamlit_stub.rerun = lambda: None
    streamlit_stub.markdown = lambda *args, **kwargs: None
    streamlit_stub.button = lambda *args, **kwargs: False
    streamlit_stub.text_input = lambda *args, **kwargs: ""
    streamlit_stub.text_area = lambda *args, **kwargs: ""
    streamlit_stub.selectbox = lambda *args, **kwargs: None
    streamlit_stub.multiselect = lambda *args, **kwargs: []
    streamlit_stub.radio = lambda *args, **kwargs: "Não"
    streamlit_stub.columns = lambda *args, **kwargs: [DummyContainer(), DummyContainer(), DummyContainer()]
    streamlit_stub.expander = lambda *args, **kwargs: None
    streamlit_stub.form = lambda *args, **kwargs: DummyContainer()
    streamlit_stub.form_submit_button = lambda *args, **kwargs: False
    streamlit_stub.dataframe = lambda *args, **kwargs: None
    streamlit_stub.metric = lambda *args, **kwargs: None
    streamlit_stub.sidebar = types.SimpleNamespace()
    streamlit_stub.set_page_config = lambda *args, **kwargs: None
    streamlit_stub.caption = lambda *args, **kwargs: None
    streamlit_stub.write = lambda *args, **kwargs: None
    streamlit_stub.download_button = lambda *args, **kwargs: None
    streamlit_stub.tabs = lambda *args, **kwargs: []
    streamlit_stub.spinner = lambda *args, **kwargs: None
    streamlit_stub.progress = lambda *args, **kwargs: None

    sys.modules["streamlit"] = streamlit_stub
    sys.modules["streamlit_geolocation"] = types.SimpleNamespace(streamlit_geolocation=lambda *args, **kwargs: None)
    sys.modules["streamlit_folium"] = types.SimpleNamespace(st_folium=lambda *args, **kwargs: None)
    sys.modules["pydeck"] = types.SimpleNamespace()
    sys.modules["folium"] = types.SimpleNamespace()

    spec = importlib.util.spec_from_file_location("app_module", Path(__file__).resolve().parents[1] / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_carregar_voluntarios_neon_returns_dataframe(monkeypatch):
    app = load_app_module()

    expected = pd.DataFrame([
        {
            "id_voluntario": 1,
            "nome": "Ana",
            "telefone": "(32) 99999-0000",
            "email": "ana@example.com",
            "cep": "36000-000",
            "endereco": "Rua A",
            "possui_veiculo": True,
            "tipo_veiculo": "Carro",
            "dias_disponiveis": "Sábado",
            "horario_inicio": "08:00",
            "horario_fim": "12:00",
            "observacoes": "Disponível",
            "data_cadastro": "2026-01-01",
            "ativo": True,
        }
    ])

    monkeypatch.setattr(app, "get_engine", lambda: object())
    monkeypatch.setattr(app.pd, "read_sql_query", lambda query, engine, params=None: expected)

    result = app.carregar_voluntarios_neon()

    assert not result.empty
    assert result.iloc[0]["nome"] == "Ana"


def test_todos_os_perfis_tem_acesso_a_familias():
    app = load_app_module()

    for perfil in set(app.PERFIS_DISPONIVEIS.values()):
        abas = app.obter_abas_padrao_por_perfil(perfil)
        assert "Famílias" in abas
