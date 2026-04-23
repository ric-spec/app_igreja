# Script para popular dados iniciais da despensa no Neon
# Execute este arquivo para carregar os itens de estoque

import pandas as pd
import datetime
from sqlalchemy import create_engine

# Configurar a URL (substitua pela sua)
NEON_URL = "postgresql://neondb_owner:npg_XSbnUR2izB4C@ep-super-hall-adgq7ehk-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Dados do Catálogo (Itens disponíveis)
catalogo_data = [
    # Grãos e Cereais
    {'id_item': 1, 'nome': 'Arroz (5kg)', 'qtd_por_cesta': 1, 'categoria': 'Grãos'},
    {'id_item': 2, 'nome': 'Feijão (1kg)', 'qtd_por_cesta': 2, 'categoria': 'Grãos'},
    {'id_item': 3, 'nome': 'Macarrão (500g)', 'qtd_por_cesta': 2, 'categoria': 'Grãos'},
    {'id_item': 4, 'nome': 'Farinha de Trigo (1kg)', 'qtd_por_cesta': 1, 'categoria': 'Grãos'},
    
    # Óleos e Condimentos
    {'id_item': 5, 'nome': 'Óleo de Soja (900ml)', 'qtd_por_cesta': 1, 'categoria': 'Óleos'},
    {'id_item': 6, 'nome': 'Sal (1kg)', 'qtd_por_cesta': 1, 'categoria': 'Condimentos'},
    {'id_item': 7, 'nome': 'Açúcar (1kg)', 'qtd_por_cesta': 1, 'categoria': 'Condimentos'},
    
    # Laticínios e Proteínas
    {'id_item': 8, 'nome': 'Leite em Pó (400g)', 'qtd_por_cesta': 1, 'categoria': 'Laticínios'},
    {'id_item': 9, 'nome': 'Ovo (dúzia)', 'qtd_por_cesta': 1, 'categoria': 'Proteínas'},
    {'id_item': 10, 'nome': 'Sardinha em Lata (120g)', 'qtd_por_cesta': 1, 'categoria': 'Proteínas'},
    
    # Frutas e Vegetais
    {'id_item': 11, 'nome': 'Batata-doce (kg)', 'qtd_por_cesta': 1, 'categoria': 'Vegetais'},
    {'id_item': 12, 'nome': 'Cebola (kg)', 'qtd_por_cesta': 1, 'categoria': 'Vegetais'},
    
    # Bebidas
    {'id_item': 13, 'nome': 'Café (500g)', 'qtd_por_cesta': 1, 'categoria': 'Bebidas'},
    {'id_item': 14, 'nome': 'Achocolatado (400g)', 'qtd_por_cesta': 1, 'categoria': 'Bebidas'},
    
    # Produtos de Higiene/Limpeza
    {'id_item': 15, 'nome': 'Sabão em Pó (500g)', 'qtd_por_cesta': 1, 'categoria': 'Higiene'},
    {'id_item': 16, 'nome': 'Desinfetante (1L)', 'qtd_por_cesta': 1, 'categoria': 'Limpeza'},
    {'id_item': 17, 'nome': 'Sabonete (unidade)', 'qtd_por_cesta': 1, 'categoria': 'Higiene'},
]

# Dados de Estoque (Lotes disponíveis)
lotes_data = [
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
]

def popular_catalogo():
    """Popula a tabela de catálogo no Neon"""
    try:
        engine = create_engine(NEON_URL)
        df_catalogo = pd.DataFrame(catalogo_data)
        
        # Insere dados (append = adiciona, replace = substitui tudo)
        df_catalogo.to_sql('catalogo', engine, if_exists='append', index=False)
        
        print(f"✅ {len(df_catalogo)} itens inseridos na tabela 'catalogo'")
        return True
    except Exception as e:
        print(f"❌ Erro ao inserir catálogo: {e}")
        return False

def popular_lotes():
    """Popula a tabela de lotes/estoque no Neon"""
    try:
        engine = create_engine(NEON_URL)
        df_lotes = pd.DataFrame(lotes_data)
        
        # Insere dados
        df_lotes.to_sql('lotes', engine, if_exists='append', index=False)
        
        print(f"✅ {len(df_lotes)} lotes inseridos na tabela 'lotes'")
        return True
    except Exception as e:
        print(f"❌ Erro ao inserir lotes: {e}")
        return False

def mostrar_disponibilidade():
    """Mostra a disponibilidade total de cada item"""
    import pandas as pd
    
    df_catalogo = pd.DataFrame(catalogo_data)
    df_lotes = pd.DataFrame(lotes_data)
    
    # Agrupa por item e soma quantidades
    disponibilidade = df_lotes.groupby('id_item')['quantidade'].sum().reset_index()
    disponibilidade.columns = ['id_item', 'quantidade_total']
    
    # Junta com catálogo para ter nomes
    resultado = pd.merge(disponibilidade, df_catalogo[['id_item', 'nome', 'categoria']], on='id_item')
    resultado = resultado.sort_values('nome')
    
    print("\n" + "="*70)
    print("📊 DISPONIBILIDADE DE ITENS NA DESPENSA")
    print("="*70)
    
    for categoria in resultado['categoria'].unique():
        print(f"\n📦 {categoria.upper()}")
        print("-" * 70)
        
        items_categoria = resultado[resultado['categoria'] == categoria]
        for _, item in items_categoria.iterrows():
            print(f"  • {item['nome']:<40} → {item['quantidade_total']:>3} unidades")
    
    print("\n" + "="*70)
    print(f"TOTAL DE ITENS: {len(resultado)}")
    print(f"TOTAL DE UNIDADES: {resultado['quantidade_total'].sum()}")
    print("="*70 + "\n")

if __name__ == "__main__":
    print("\n🗄️ SCRIPT DE POPULAÇÃO DE DADOS DA DESPENSA\n")
    
    # Mostrar disponibilidade primeiro
    mostrar_disponibilidade()
    
    # Perguntar se quer inserir no Neon
    print("Você deseja inserir esses dados no Neon?")
    print("(Certifique-se de ter atualizado NEON_URL com sua URL real)")
    resposta = input("Digite 's' para sim ou 'n' para não: ").lower()
    
    if resposta == 's':
        print("\n⏳ Inserindo dados no Neon...")
        
        if popular_catalogo():
            popular_lotes()
            print("\n✅ Dados da despensa inseridos com sucesso!")
        else:
            print("\n⚠️ Falha ao inserir dados. Verifique sua URL do Neon.")
    else:
        print("\n✋ Operação cancelada.")
        print("   Para inserir depois, execute: python popular_despensa.py")
