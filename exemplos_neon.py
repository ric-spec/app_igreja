# EXEMPLOS DE USO - Salvando dados no Neon
# Este arquivo mostra como usar as funções de salvar dados ao Neon

import pandas as pd
import datetime
from datetime import datetime as dt

# ==========================================
# EXEMPLO 1: Salvar uma Nova Família
# ==========================================
def exemplo_salvar_familia():
    """
    Exemplo de como salvar uma nova família no Neon
    """
    dados_familia = {
        'nome': 'Maria de Fátima Silva',
        'dependentes': 3,
        'prioridade': 'Alta',
        'cep': '36010001',
        'endereco': 'Av. Barão do Rio Branco, 100 - Centro, Juiz de Fora/MG',
        'lat': -21.7611,
        'lon': -43.3444,
        'igreja': 'Igreja Batista Central',
        'pastor': 'Pr. Carlos',
        'ultima_entrega': None
    }
    
    # Chamar função para salvar
    # salvar_familia_neon(dados_familia)
    print("✅ Família salva com sucesso!")
    print(f"   Nome: {dados_familia['nome']}")
    print(f"   Dependentes: {dados_familia['dependentes']}")

# ==========================================
# EXEMPLO 2: Registrar uma Entrega
# ==========================================
def exemplo_salvar_entrega():
    """
    Exemplo de como registrar uma entrega no Neon
    """
    dados_entrega = {
        'id_entrega': 1,
        'nome_familia': 'Maria de Fátima Silva',
        'data': datetime.date.today(),
        'tipo': 'Cesta Padrão',
        'responsavel_entrega': 'João da Silva'
    }
    
    # Chamar função para salvar
    # salvar_entrega_neon(dados_entrega)
    print("✅ Entrega registrada com sucesso!")
    print(f"   Família: {dados_entrega['nome_familia']}")
    print(f"   Data: {dados_entrega['data']}")

# ==========================================
# EXEMPLO 3: Registrar SOS/WhatsApp
# ==========================================
def exemplo_salvar_sos():
    """
    Exemplo de como registrar um pedido de SOS/WhatsApp
    """
    dados_sos = {
        'telefone': '(32) 98888-1234',
        'nome': 'Ana Souza',
        'necessidade': 'Abrigo',
        'pessoas': 4,
        'cep': '36010001',
        'status': 'Pendente',
        'data_hora': datetime.datetime.now()
    }
    
    # Chamar função para salvar
    # salvar_sos_neon(dados_sos)
    print("✅ SOS registrado com sucesso!")
    print(f"   Pessoa: {dados_sos['nome']}")
    print(f"   Necessidade: {dados_sos['necessidade']}")
    print(f"   Pessoas: {dados_sos['pessoas']}")

# ==========================================
# EXEMPLO 4: Registrar Acolhimento
# ==========================================
def exemplo_salvar_acolhimento():
    """
    Exemplo de como registrar um acolhimento no Neon
    """
    dados_acolhimento = {
        'id_acolhido': 1,
        'id_local': 1,
        'nome_responsavel': 'João Silva',
        'qtd_pessoas': 4,
        'cep_origem': '36010001',
        'endereco_origem': 'Rua X, 123',
        'lat_origem': -21.7611,
        'lon_origem': -43.3444,
        'data_entrada': datetime.datetime.now(),
        'responsavel_checkin': 'Admin'
    }
    
    # Chamar função para salvar
    # salvar_acolhimento_neon(dados_acolhimento)
    print("✅ Acolhimento registrado com sucesso!")
    print(f"   Responsável: {dados_acolhimento['nome_responsavel']}")
    print(f"   Pessoas: {dados_acolhimento['qtd_pessoas']}")

# ==========================================
# EXEMPLO 5: Salvar Atendimento Genérico
# ==========================================
def exemplo_salvar_atendimento():
    """
    Exemplo de como salvar um atendimento genérico
    """
    dados_atendimento = {
        'pessoa_nome': 'José da Silva',
        'tipo_atendimento': 'Consulta Médica',
        'descricao': 'Atendimento de rotina realizado com sucesso',
        'data_atendimento': datetime.datetime.now(),
        'status': 'Concluído',
        'responsavel': 'Dr. Fernando'
    }
    
    # Chamar função para salvar
    # salvar_atendimento_neon(dados_atendimento)
    print("✅ Atendimento registrado com sucesso!")
    print(f"   Pessoa: {dados_atendimento['pessoa_nome']}")
    print(f"   Tipo: {dados_atendimento['tipo_atendimento']}")

# ==========================================
# INTEGRAÇÃO COM STREAMLIT (NO app.py)
# ==========================================
def exemplo_integracao_streamlit():
    """
    Exemplo de como integrar com Streamlit
    """
    codigo_exemplo = """
import streamlit as st
import pandas as pd

# ... seu código Streamlit ...

# Quando o usuário preenche o formulário:
with st.form("form_familia"):
    nome = st.text_input("Nome")
    dependentes = st.number_input("Dependentes")
    
    if st.form_submit_button("Cadastrar"):
        # Dados da família
        dados_familia = {
            'nome': nome,
            'dependentes': dependentes,
            # ... outros campos ...
        }
        
        # 1. Salva em memória (session_state)
        st.session_state.db_familias = pd.concat([
            st.session_state.db_familias,
            pd.DataFrame([dados_familia])
        ], ignore_index=True)
        
        # 2. Salva no Neon (automático)
        salvar_familia_neon(dados_familia)
        
        st.success("Família cadastrada com sucesso!")
    """
    print(codigo_exemplo)

# ==========================================
# QUERIES SQL ÚTEIS
# ==========================================
def exemplos_sql():
    """
    Exemplos de queries SQL para consultar dados no Neon
    """
    queries = {
        'Listar todas as famílias': """
            SELECT id_familia, nome, dependentes, prioridade, endereco
            FROM familias
            ORDER BY data_cadastro DESC
            LIMIT 10;
        """,
        'Contar entregas por família': """
            SELECT nome_familia, COUNT(*) as total_entregas
            FROM entregas
            GROUP BY nome_familia
            ORDER BY total_entregas DESC;
        """,
        'SOS pendentes': """
            SELECT id_msg, nome, necessidade, pessoas, data_hora
            FROM sos_whatsapp
            WHERE status = 'Pendente'
            ORDER BY data_hora DESC;
        """,
        'Ocupação de abrigos': """
            SELECT la.nome, COUNT(*) as pessoas_abrigadas, la.capacidade
            FROM pessoas_abrigadas pa
            JOIN locais_acolhimento la ON pa.id_local = la.id_local
            GROUP BY la.nome, la.capacidade;
        """,
        'Histórico de acolhimentos': """
            SELECT pa.nome_responsavel, pa.qtd_pessoas, 
                   la.nome as local, pa.data_entrada
            FROM pessoas_abrigadas pa
            JOIN locais_acolhimento la ON pa.id_local = la.id_local
            ORDER BY pa.data_entrada DESC;
        """
    }
    
    for descricao, query in queries.items():
        print(f"\n{'='*50}")
        print(f"📊 {descricao}")
        print(f"{'='*50}")
        print(query)

# ==========================================
# EXECUTAR EXEMPLOS
# ==========================================
if __name__ == "__main__":
    print("="*60)
    print("EXEMPLOS DE USO - INTEGRAÇÃO COM NEON")
    print("="*60)
    
    print("\n1️⃣ SALVAR FAMÍLIA")
    print("-"*60)
    exemplo_salvar_familia()
    
    print("\n2️⃣ REGISTRAR ENTREGA")
    print("-"*60)
    exemplo_salvar_entrega()
    
    print("\n3️⃣ REGISTRAR SOS")
    print("-"*60)
    exemplo_salvar_sos()
    
    print("\n4️⃣ REGISTRAR ACOLHIMENTO")
    print("-"*60)
    exemplo_salvar_acolhimento()
    
    print("\n5️⃣ SALVAR ATENDIMENTO")
    print("-"*60)
    exemplo_salvar_atendimento()
    
    print("\n6️⃣ QUERIES SQL ÚTEIS")
    print("-"*60)
    exemplos_sql()
    
    print("\n" + "="*60)
    print("✅ Para usar no seu app, descomente as chamadas das funções")
    print("   Elas já foram adicionadas automaticamente!")
    print("="*60)
