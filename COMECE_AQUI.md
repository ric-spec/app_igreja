# 🚀 INÍCIO RÁPIDO - Integração com Neon em 3 Passos

## ⚡ Faça Agora (5 minutos)

### Passo 1: Copie sua URL do Neon
```
1. Acesse https://console.neon.tech
2. Copie a URL de conexão PostgreSQL
3. Pareça: postgresql://usuario:senha@host/banco?sslmode=require
```

### Passo 2: Cole a URL no arquivo
```bash
# Edite .streamlit/secrets.toml
# Cole sua URL aqui:

[postgres]
url = "COLE_SUA_URL_AQUI"
```

### Passo 3: Crie as Tabelas
```bash
# Opção A: No Neon Dashboard
1. SQL Editor
2. Copie tudo de: migrations.sql
3. Execute

# Opção B: Pelo terminal
pip install sqlalchemy psycopg2-binary
python test_neon_connection.py
```

## ✅ Pronto!

```bash
pip install -r requirements.txt
streamlit run app.py
```

Quando você cadastrar uma família, os dados vão aparecer automaticamente no Neon! ✨

---

## 📚 Ler Depois (em ordem)

1. **[README_NEON.md](README_NEON.md)** - Visão geral
2. **[NEON_SETUP.md](NEON_SETUP.md)** - Guia detalhado
3. **[CHECKLIST.md](CHECKLIST.md)** - Passo a passo completo
4. **[exemplos_neon.py](exemplos_neon.py)** - Exemplos de código

---

## 🆘 Problema?

Está preso? Execute:
```bash
python test_neon_connection.py
```

Ele dirá exatamente qual é o problema e como corrigir!

---

**Fim! Sua app agora salva dados no Neon! 🎉**
