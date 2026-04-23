# 🔗 Configuração de Conexão com Neon

Esta documentação explica como configurar e usar a conexão com o banco de dados PostgreSQL no Neon.

## 📋 Pré-requisitos

1. **Conta no Neon**: Crie uma conta em [https://neon.tech](https://neon.tech)
2. **Pacotes instalados**: 
   ```bash
   pip install sqlalchemy psycopg2-binary streamlit
   ```

## 🔑 Configuração dos Secrets

O arquivo `.streamlit/secrets.toml` já está criado. Siga estes passos:

### 1. Obter a URL de Conexão do Neon

1. Acesse seu dashboard no Neon
2. Selecione seu projeto
3. Copie a **Connection String** do PostgreSQL
4. Deve parecer assim:
   ```
   postgresql://neondb_owner:sua-senha@seu-host/seu-banco?sslmode=require&channel_binding=require
   ```

### 2. Atualizar o arquivo secrets.toml

Edite `.streamlit/secrets.toml` e substitua a URL:

```toml
[postgres]
url = "postgresql://seu-usuario:sua-senha@seu-host/seu-banco?sslmode=require&channel_binding=require"
```

## 🗄️ Criar as Tabelas no Neon

### Opção 1: Usar o SQL Editor do Neon

1. Acesse o Neon Dashboard
2. Clique em **SQL Editor**
3. Copie e cole o conteúdo do arquivo `migrations.sql`
4. Execute o script

### Opção 2: Usar a CLI do Neon

```bash
neon connect -c "cat migrations.sql" | psql
```

### Opção 3: Usar Python localmente

```python
from sqlalchemy import create_engine

# Configure a URL no arquivo secrets.toml
import streamlit as st
conn_url = st.secrets["postgres"]["url"]
engine = create_engine(conn_url)

# Leia e execute o arquivo SQL
with open('migrations.sql', 'r') as f:
    sql = f.read()
    with engine.connect() as connection:
        connection.execute(sql)
        connection.commit()
```

## 📊 Funções Disponíveis

O `app.py` já possui as seguintes funções prontas para salvar dados:

### 1. `salvar_familia_neon(dados_familia)`
Salva uma nova família no banco de dados.

```python
dados_familia = {
    'nome': 'Maria de Fátima',
    'dependentes': 3,
    'prioridade': 'Alta',
    'cep': '36010001',
    'endereco': 'Av. Barão do Rio Branco, 100',
    'lat': -21.7611,
    'lon': -43.3444,
    'igreja': 'Igreja Batista Central',
    'pastor': 'Pr. Carlos'
}
salvar_familia_neon(dados_familia)
```

### 2. `salvar_entrega_neon(dados_entrega)`
Registra uma entrega realizada.

```python
dados_entrega = {
    'id_familia': 1,
    'nome_familia': 'Maria de Fátima',
    'data': datetime.datetime.now(),
    'tipo': 'Cesta Básica',
    'responsavel_entrega': 'João da Silva'
}
salvar_entrega_neon(dados_entrega)
```

### 3. `salvar_sos_neon(dados_sos)`
Registra um pedido de SOS via WhatsApp.

```python
dados_sos = {
    'telefone': '(32) 98888-1234',
    'nome': 'Ana Souza',
    'necessidade': 'Abrigo',
    'pessoas': 4,
    'cep': '36010001',
    'status': 'Pendente',
    'data_hora': datetime.datetime.now()
}
salvar_sos_neon(dados_sos)
```

### 4. `salvar_acolhimento_neon(dados_acolhimento)`
Registra um acolhimento em um local de abrigo.

```python
dados_acolhimento = {
    'id_local': 1,
    'nome_responsavel': 'João Silva',
    'qtd_pessoas': 4,
    'cep_origem': '36010001',
    'endereco_origem': 'Rua X',
    'data_entrada': datetime.datetime.now(),
    'responsavel_checkin': 'Admin'
}
salvar_acolhimento_neon(dados_acolhimento)
```

### 5. `salvar_atendimento_neon(dados)`
Função genérica para salvar qualquer atendimento.

```python
dados = {
    'pessoa_nome': 'Maria',
    'tipo_atendimento': 'Consulta Médica',
    'descricao': 'Atendimento realizado com sucesso',
    'data_atendimento': datetime.datetime.now(),
    'status': 'Concluído',
    'responsavel': 'Dr. Silva'
}
salvar_atendimento_neon(dados)
```

## 🔄 Integração com o App

As funções já estão prontas para usar em qualquer lugar do código Streamlit:

```python
# Após criar um novo registro em session_state, 
# também salve no Neon:

novo = {
    'nome': 'Nova Família',
    'dependentes': 2,
    # ... outros campos
}

# Salva em memória
st.session_state.db_familias = pd.concat([
    st.session_state.db_familias, 
    pd.DataFrame([novo])
], ignore_index=True)

# Salva no Neon
salvar_familia_neon(novo)
```

## 🧪 Testar a Conexão

Execute no terminal:

```bash
streamlit run app.py
```

Se a conexão estiver funcionando, você verá mensagens de sucesso ao salvar dados.

## 🐛 Solução de Problemas

### Erro: "Secrets file not found"
- Certifique-se de que `.streamlit/secrets.toml` existe
- Reinicie o Streamlit: `streamlit run app.py`

### Erro: "Connection refused"
- Verifique se a URL do Neon está correta
- Confirme que sua conta Neon está ativa
- Veja se o firewall permite conexões do seu IP

### Erro: "Table already exists"
- O script SQL cria tabelas apenas se não existirem (`CREATE TABLE IF NOT EXISTS`)
- Para resetar, delete a tabela no Dashboard do Neon e execute novamente

### Aviso: "Erro ao salvar no Neon"
- Os dados são salvos em memória (session_state) mesmo se o Neon falhar
- Verifique a conexão de internet
- Veja os logs do Streamlit: `streamlit run app.py --logger.level=debug`

## 📚 Recursos

- [Documentação do Neon](https://neon.tech/docs)
- [SQLAlchemy Pandas Integration](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html)
- [Streamlit Secrets Management](https://docs.streamlit.io/develop/api-reference/connections/secrets)

## 🚀 Deploy em Produção

Ao fazer deploy no Streamlit Cloud ou outro host:

1. **Neon Secrets**: Configure os secrets no dashboard da plataforma
2. **Firewall**: Adicione o IP da plataforma às permissões do Neon
3. **Pool de Conexões**: Use o URL de pool do Neon para permitir múltiplas conexões

```toml
# Para Streamlit Cloud, use o Pool Connector
[postgres]
url = "postgresql://...pooler.neon.tech/..."  # Note o "pooler"
```

---

**✅ Pronto!** Seu app agora está conectado ao Neon! 🎉
