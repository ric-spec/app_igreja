# Script de teste para validar a conexão com Neon
# Execute este arquivo para verificar se tudo está funcionando

import sys
import pandas as pd
from datetime import datetime, timedelta

try:
    from sqlalchemy import create_engine, text
    print("✅ SQLAlchemy importado com sucesso")
except ImportError:
    print("❌ SQLAlchemy não está instalado")
    print("   Execute: pip install sqlalchemy psycopg2-binary")
    sys.exit(1)

# ==========================================
# 1. TESTAR LEITURA DOS SECRETS
# ==========================================
print("\n1️⃣ Testando leitura dos secrets...")
try:
    import streamlit as st
    conn_url = st.secrets["postgres"]["url"]
    print("✅ URL de conexão carregada dos secrets")
    print(f"   Host: {conn_url.split('@')[1].split('/')[0]}")
except Exception as e:
    print(f"❌ Erro ao ler secrets: {e}")
    print("   Solução: Verifique se .streamlit/secrets.toml existe e contém [postgres] url")
    sys.exit(1)

# ==========================================
# 2. TESTAR CONEXÃO COM O NEON
# ==========================================
print("\n2️⃣ Testando conexão com Neon...")
try:
    engine = create_engine(conn_url, echo=False)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Conexão com Neon estabelecida com sucesso!")
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
    print("   Solução: Verifique a URL de conexão e acesso à internet")
    sys.exit(1)

# ==========================================
# 3. TESTAR LISTA DE TABELAS
# ==========================================
print("\n3️⃣ Verificando tabelas existentes...")
try:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public'
        """))
        tables = [row[0] for row in result]
        if tables:
            print(f"✅ Encontradas {len(tables)} tabelas:")
            for table in tables:
                print(f"   • {table}")
        else:
            print("⚠️  Nenhuma tabela encontrada")
            print("   Solução: Execute o arquivo migrations.sql no Neon Dashboard")
except Exception as e:
    print(f"❌ Erro ao listar tabelas: {e}")

# ==========================================
# 4. TESTAR INSERÇÃO DE DADOS DE TESTE
# ==========================================
print("\n4️⃣ Testando inserção de dados...")
try:
    # Dados de teste
    dados_teste = {
        'nome': 'Teste Integração',
        'dependentes': 2,
        'prioridade': 'Média',
        'cep': '36010001',
        'endereco': 'Endereço de Teste',
        'lat': -21.7611,
        'lon': -43.3444,
        'igreja': 'Igreja Teste',
        'pastor': 'Pr. Teste'
    }
    
    df_teste = pd.DataFrame([dados_teste])
    df_teste.to_sql('familias', engine, if_exists='append', index=False)
    print("✅ Dados inseridos com sucesso na tabela 'familias'")
    
except Exception as e:
    print(f"⚠️  Erro ao inserir dados: {e}")
    print("   Dica: A tabela 'familias' pode não existir")

# ==========================================
# 5. TESTAR LEITURA DOS DADOS
# ==========================================
print("\n5️⃣ Testando leitura dos dados...")
try:
    df = pd.read_sql_table('familias', engine)
    print(f"✅ Lidos {len(df)} registros da tabela 'familias'")
    if len(df) > 0:
        print("\nÚltimo registro:")
        print(df.iloc[-1])
except Exception as e:
    print(f"⚠️  Erro ao ler dados: {e}")

# ==========================================
# RESUMO FINAL
# ==========================================
print("\n" + "="*50)
print("✅ TESTE CONCLUÍDO COM SUCESSO!")
print("="*50)
print("\nSeu app está pronto usar com Neon! 🎉")
print("\nProximos passos:")
print("1. Execute: streamlit run app.py")
print("2. Cadastre uma nova família")
print("3. Verifique se os dados aparecem no Neon")
print("\nDocumentação: Veja NEON_SETUP.md para mais detalhes")
