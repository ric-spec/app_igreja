# 🔗 Integração Neon - App Igreja

Sua aplicação Streamlit foi configurada para salvar dados no banco PostgreSQL do **Neon**!

## ⚡ Quick Start (3 passos)

### 1️⃣ Atualizar a URL
Edite `.streamlit/secrets.toml`:
```toml
[postgres]
url = "postgresql://seu-usuario:sua-senha@seu-host/seu-banco?sslmode=require"
```

### 2️⃣ Instalar e Criar Tabelas
```bash
pip install -r requirements.txt

# Depois, execute o SQL em migrations.sql no Neon Dashboard
```

### 3️⃣ Testar
```bash
python test_neon_connection.py
streamlit run app.py
```

## 📦 O que foi adicionado?

✅ **Imports**: SQLAlchemy + psycopg2 adicionados  
✅ **Funções**: 6 funções de salvar dados  
✅ **Integração**: Chamadas automáticas nos formulários  
✅ **Secrets**: Arquivo `.streamlit/secrets.toml` criado  
✅ **Banco de Dados**: Schema SQL em `migrations.sql`  

## 🔄 Fluxo Automático

```
Usuário preenche formulário
        ↓
Salva em session_state (memória)
        ↓
Salva no Neon (banco de dados)
        ↓
✅ Sucesso!
```

## 📂 Arquivos Novos/Modificados

| Arquivo | Tipo | O que faz? |
|---------|------|-----------|
| `requirements.txt` | 🔄 Modificado | Adicionadas dependências |
| `app.py` | 🔄 Modificado | Adicionadas funções de conexão |
| `.streamlit/secrets.toml` | ✨ Novo | Config de conexão ao Neon |
| `migrations.sql` | ✨ Novo | Script para criar tabelas |
| `test_neon_connection.py` | ✨ Novo | Teste de conexão |
| `exemplos_neon.py` | ✨ Novo | Exemplos de uso |
| `NEON_SETUP.md` | ✨ Novo | Guia detalhado (⭐ LEIA PRIMEIRO) |
| `INTEGRACAO_NEON.md` | ✨ Novo | Resumo das mudanças |
| `CHECKLIST.md` | ✨ Novo | Instruções passo a passo |

## 🎯 Dados Sincronizados

Quando o usuário:
- ✅ **Cadastra família** → Salva em `familias`
- ✅ **Realiza entrega** → Salva em `entregas`
- ✅ **Registra acolhimento** → Salva em `pessoas_abrigadas`
- ✅ **Outros dados** → Pode usar `salvar_atendimento_neon()`

## 🚀 Deploy Rápido

### Local
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Streamlit Cloud
1. Suba o repo no GitHub
2. Connect no Streamlit Cloud
3. Adicione secrets lá também

## 🔍 Verificar Dados no Neon

No Neon Dashboard:
1. SQL Editor
2. Execute:
```sql
SELECT COUNT(*) FROM familias;
SELECT * FROM entregas LIMIT 5;
```

## 🆘 Problemas?

| Erro | Solução |
|------|---------|
| `ModuleNotFoundError: sqlalchemy` | `pip install sqlalchemy psycopg2-binary` |
| `Secrets file not found` | Arquivo já existe: `.streamlit/secrets.toml` |
| `Connection refused` | Verifique URL e execute `python test_neon_connection.py` |
| Dados não salvam | Verifique tabelas com `python test_neon_connection.py` |

## 📖 Leitura Recomendada

1. **[NEON_SETUP.md](NEON_SETUP.md)** ⭐ COMECE POR AQUI
   - Configuração passo a passo
   - FAQ completo
   - Exemplos práticos

2. **[CHECKLIST.md](CHECKLIST.md)**
   - Checklist de implementação
   - Scripts de teste
   - Troubleshooting

3. **[exemplos_neon.py](exemplos_neon.py)**
   - Código pronto para copiar
   - Queries SQL úteis

## 💡 Exemplo Rápido

```python
# No seu app.py, já está assim:

# Quando usuario cadastra familia
nova_fam = {
    'nome': 'Maria',
    'dependentes': 3,
    # ...
}

# Salva em memória
st.session_state.db_familias = pd.concat([...])

# Salva no Neon (automático!)
salvar_familia_neon(nova_fam)
```

## ✨ Funcionalidades

- 📱 Interface Streamlit existente + Neon
- 💾 Dados salvos em memória E banco de dados
- 🔒 Senhas seguras em secrets.toml
- 📊 Backup automático no Neon
- ⚡ Fallback se Neon falhar (dados permanecem em session_state)

## 📞 Próximas Otimizações (Opcional)

- [ ] Carregar dados do Neon ao iniciar app
- [ ] Dashboard com analytics do Neon
- [ ] Backup automático diário
- [ ] Sincronização bi-direcional
- [ ] API REST para dados do Neon

---

**Pronto para usar! 🎉**

Siga os **3 passos do Quick Start** lá em cima e seu app estará conectado ao Neon.

**Dúvidas?** Veja [NEON_SETUP.md](NEON_SETUP.md)
