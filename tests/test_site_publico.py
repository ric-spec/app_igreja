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


def load_site_module():
    streamlit_stub = types.ModuleType("streamlit")
    streamlit_stub.session_state = SessionStateProxy()
    streamlit_stub.cache_resource = lambda func: func
    streamlit_stub.cache_data = lambda *args, **kwargs: (lambda func: _memoized(func))
    streamlit_stub.set_page_config = lambda *args, **kwargs: None
    streamlit_stub.markdown = lambda *args, **kwargs: None
    streamlit_stub.warning = lambda *args, **kwargs: None
    streamlit_stub.success = lambda *args, **kwargs: None
    streamlit_stub.error = lambda *args, **kwargs: None
    streamlit_stub.image = lambda *args, **kwargs: None
    streamlit_stub.columns = lambda *args, **kwargs: [DummyContainer(), DummyContainer(), DummyContainer()]
    streamlit_stub.button = lambda *args, **kwargs: False
    streamlit_stub.spinner = lambda *args, **kwargs: (lambda f: f)
    streamlit_stub.form = lambda *args, **kwargs: DummyContainer()
    streamlit_stub.form_submit_button = lambda *args, **kwargs: False
    streamlit_stub.text_input = lambda *args, **kwargs: ""
    streamlit_stub.selectbox = lambda *args, **kwargs: None
    streamlit_stub.number_input = lambda *args, **kwargs: 0
    streamlit_stub.radio = lambda *args, **kwargs: None
    streamlit_stub.balloons = lambda *args, **kwargs: None
    streamlit_stub.caption = lambda *args, **kwargs: None
    streamlit_stub.write = lambda *args, **kwargs: None
    streamlit_stub.metric = lambda *args, **kwargs: None
    streamlit_stub.expander = lambda *args, **kwargs: DummyContainer()
    streamlit_stub.download_button = lambda *args, **kwargs: None
    streamlit_stub.secrets = {}

    sys.modules["streamlit"] = streamlit_stub
    sys.modules["matplotlib"] = types.ModuleType("matplotlib")
    sys.modules["matplotlib.pyplot"] = types.ModuleType("matplotlib.pyplot")

    spec = importlib.util.spec_from_file_location("site_publico_test", Path(__file__).resolve().parents[1] / "site_publico.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _memoized(func):
    cache = {}

    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper


def test_catalogo_usa_dados_frescos(monkeypatch):
    module = load_site_module()
    monkeypatch.setattr(module, "get_engine", lambda: object())

    calls = []

    def fake_read_sql_query(query, engine, params=None):
        calls.append(query)
        return pd.DataFrame([
            {"id_item": 1, "nome": "Arroz", "qtd_por_cesta": 2, "categoria": "Cesta"}
        ])

    monkeypatch.setattr(module.pd, "read_sql_query", fake_read_sql_query)

    first = module.carregar_catalogo_neon()
    second = module.carregar_catalogo_neon()

    assert not first.empty
    assert not second.empty
    assert len(calls) == 2


def test_formatar_item_em_negrito_remove_espacos_e_escapa_html():
    module = load_site_module()

    markup = module.formatar_item_para_destaque("Ervilha ")

    assert "<strong>Ervilha</strong>" in markup
    assert "&lt;" not in markup
